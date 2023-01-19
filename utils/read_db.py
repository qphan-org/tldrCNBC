import requests
import json
from pprint import pprint
from bson.json_util import dumps as bson_dumps

config_file = open("config.json", "r")
config = json.load(config_file)
db_api_key = config['db_api_key']
TESTING_MODE = config['TESTING_MODE']

# test data
test_data_file = open("test_data.json","r")
test_data = json.load(test_data_file)


def read_db(query: dict = {}, limit: int=32, skip: int = 0):
    # if testing mode is ON, then return a testing dataset
    if TESTING_MODE:
        return test_data
    
    # inject additional query to the input query
    final_query = {
        '$and' : [
            {"article_length": {"$gt":10}},
            {"publish_timestamp": {"$gte":'2023-01-01'}},
            {"$or" : 
                [
                    {"sentiment.Sentiment" : "NEGATIVE"},      
                    {"sentiment.Sentiment" : "NEUTRAL"},      
                    {"sentiment.Sentiment" : "POSITIVE"},      
                    {"sentiment.Sentiment" : "MIXED"},      
                ]
            },
            query,
        ]
    }
    
    url = "https://data.mongodb-api.com/app/data-ytlfz/endpoint/data/beta/action/find"
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
            
        },
        "sort": {"publish_timestamp": -1},
        "limit": limit,
        "skip": limit * skip,
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': db_api_key,
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.content)['documents']
    return results

def read_one(query: dict = {}):
    # if testing mode is ON, then return a testing dataset
    if TESTING_MODE:
        return test_data
    
    url = "https://data.mongodb-api.com/app/data-ytlfz/endpoint/data/beta/action/findOne"
    payload = bson_dumps({
        "collection": "news",
        "database": "ruby",
        "dataSource": "ruby-1",
        "filter": query,
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
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': db_api_key,
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.content)
    document = results['document']
    return document

def get_count(query: dict = {}):
    # if testing mode is ON, then return a testing dataset
    if TESTING_MODE:
        return test_data
    
    # inject additional query to the input query
    final_query = {
        '$and' : [
            {"article_length": {"$gt":10}},
            {"publish_timestamp": {"$gte":'2023-01-01'}},
            {"$or" : 
                [
                    {"sentiment.Sentiment" : "NEGATIVE"},      
                    {"sentiment.Sentiment" : "NEUTRAL"},      
                    {"sentiment.Sentiment" : "POSITIVE"},      
                    {"sentiment.Sentiment" : "MIXED"},      
                ]
            },
            query,
        ]
    }
    
    url = "https://data.mongodb-api.com/app/data-ytlfz/endpoint/data/beta/action/find"
    payload = json.dumps({
        "collection": "news",
        "database": "ruby",
        "dataSource": "ruby-1",
        "filter": final_query,
        "projection": {
            '_id': 1,
            
        },
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': db_api_key,
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.content)['documents']
    return len(results)

if __name__ == '__main__':
    pass