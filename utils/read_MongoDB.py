import requests
import json
from pprint import pprint
from bson.json_util import dumps as bson_dumps

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    db_api_key      = config['db_api_key']
    dp_api_id       = config['db_api_id']
    TESTING_MODE    = config['TESTING_MODE']

# test data
with open("test_data.json","r") as test_data_file:
    test_data = json.load(test_data_file)


headers = {
    'Content-Type'                  : 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key'                       : db_api_key,
    'Accept'                        : 'application/json'
}

def get_final_query(query: str, start_date: str = '2023-01-01'):
    return {
        '$and' : [
            {"publish_timestamp": {"$gte":start_date}},
            {"article_length": {"$lte":2500}},
            {"sentiment.Sentiment" : {'$ne':"OVERFLOW"}},
            query,
        ]
    }

def get_db_mongo():
    # find all
    documents = find_all_mongo(limit=None)
    database = json.dumps(documents, indent=4)
    with open('database/frontpage_data/database.json', 'w+') as fd:
        fd.write(database)

def find_all_mongo(query: dict = {}, limit: int=32, skip: int = 0):
    # if testing mode is ON, then return a testing dataset
    if TESTING_MODE:
        return test_data
    
    # inject additional query to the input query
    final_query = get_final_query(query)
    
    url = f"https://data.mongodb-api.com/app/{dp_api_id}/endpoint/data/beta/action/find"
    
    results = list()
    
    # TODO: need to fix this to make it's more matainable
    skip = (limit if limit else 0) * skip
    
    while True:
        payload = json.dumps({
            "collection": "news",
            "database": "ruby",
            "dataSource": "ruby-1",
            "filter": final_query,
            "projection": {
                'sentiment.Sentiment': 1,
                'publish_timestamp': 1,
                'tickers' : 1,
                'title': 1,
                'keywords': 1,
            },
            "sort": {"publish_timestamp": -1},
            "limit": limit,
            "skip": skip,
        })
        
        response = requests.request("POST", url, headers=headers, data=payload)
        documents = json.loads(response.content)['documents']
        if not documents:
            break
        results += documents
        if limit and len(results) >= limit:
            break
        skip += 1000
        
    print(len(results))
    return results[:limit]

def find_one_mongo(query: dict = {}):
    # inject additional query to the input query
    final_query = get_final_query(query)
    
    url = f"https://data.mongodb-api.com/app/{dp_api_id}/endpoint/data/beta/action/findOne"
    payload = bson_dumps({
        "collection": "news",
        "database": "ruby",
        "dataSource": "ruby-1",
        "filter": final_query,
        "projection": {
            'news_url': 1,
            'sentiment': 1,
            'publish_timestamp': 1,
            'tickers' : 1,
            'title': 1,
            'tags': 1,
            'keywords': 1,
        },
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.content)
    document = results['document']
    return document

def count_mongo(query: dict = {}):
    # inject additional query to the input query
    final_query = get_final_query(query)
    
    url = f"https://data.mongodb-api.com/app/{dp_api_id}/endpoint/data/beta/action/find"
    payload = json.dumps({
        "collection": "news",
        "database": "ruby",
        "dataSource": "ruby-1",
        "filter": final_query,
        "projection": {
            '_id': 1,
            
        },
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.content)['documents']
    return len(results)

def if_exists_mongo(query: dict = {}, skip: int = 0, limit: int = 32):
    # inject additional query to the input query
    final_query = get_final_query(query)
    
    url = f"https://data.mongodb-api.com/app/{dp_api_id}/endpoint/data/beta/action/find"
    payload = bson_dumps({
        "collection": "news",
        "database": "ruby",
        "dataSource": "ruby-1",
        "filter": final_query,
        "skip": skip * limit,
        "limit": 1,
        "projection": {
            '_id': 1,
        },
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.content)
    documents = results['documents']
    return documents != []

if __name__ == '__main__':
    get_db_mongo()