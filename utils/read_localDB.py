"""
    The purpose of these functions is to reduce the api calls on the MongoDB Cloud to reduce cost
    
    Assumption: there is a local JSON file containe all necessary information
"""

from __future__ import annotations
import json
import re
from pprint import pprint
from utils import find_one_mongo
import os

def filter_documents(docs: list[dict], query: dict):
    filtered_docs = [
        doc for doc in docs 
        if all([
            # exact match kv
            (k,v) in doc.items()
            # partial match
            or (
                isinstance(doc_values := doc.get(k), list) and (
                    # search ticker
                    v in doc_values
                    
                    # search keyword using regex.match (case insensitive)
                    or isinstance(v, dict) and '$regex' in v.keys() and '$options' in v.keys()
                        and v['$options'] == 'i' 
                        and len(list(filter(re.compile(f".*{v['$regex']}").match, doc_values))) > 0
                )
            )
            for k,v in query.items()])
    ]
    return filtered_docs

def find_all_local(query: dict = {}, limit: int=32, skip: int = 0): # --> list[document]
    with open('database/frontpage_data/database.json', 'r') as f:
        documents = json.load(f)
        
    if not query:
        documents = documents[skip*limit : skip*limit + limit]
        return documents
    
    # need to filter documents to fit query
    documents = filter_documents(documents, query)
        
    # only want to return a portion of the documents
    documents = documents[skip*limit : skip*limit + limit]
    
    return documents

def find_one_local(query: dict = {}): # --> document
    file_name = str(query)
    file_path = f"./database/article_data/{file_name}.json"
    check_file = os.path.isfile(file_path)
    document = None
    
    # if the query output hasn't been stored
    if check_file:
        # open file and return the document
        with open(file_path, 'r') as f:
            document = json.load(f)
    else:
        # request it from mongodb
        document = find_one_mongo(query)
        # store it for later use
        file = json.dumps(document, indent=4)
        with open(file_path, 'w+') as f:
            f.write(file)
            
    return document
    

def count_local(query: dict = {}): # --> int
    with open('database/frontpage_data/database.json', 'r') as f:
        documents = json.load(f)
        
    if not query:
        return len(documents)
    
    # need to filter documents to fit query
    documents = filter_documents(documents, query)
    return len(documents)

def if_exists_local(query: dict = {}, skip: int = 0, limit: int = 32): # --> True/False
    return len(find_all_local(query=query, limit=limit, skip=skip)) > 0

if __name__ == '__main__':    
    pass
