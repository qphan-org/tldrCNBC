from flask import Flask, session, render_template, request, redirect, url_for
from utils import read_db, read_one
from pprint import pprint
from bson.objectid import ObjectId
import json

app = Flask('app')
app.secret_key = "leo-phan"

@app.route('/', methods=['GET', 'POST'])
def index():
    session.clear()
    articles = read_db(
        filter={
            "$and": [
                {"article_length": {"$gt":10}},
                {"$or" : 
                    [
                        {"sentiment.Sentiment" : "NEGATIVE"},      
                        {"sentiment.Sentiment" : "NEUTRAL"},      
                        {"sentiment.Sentiment" : "POSITIVE"},      
                        {"sentiment.Sentiment" : "MIXED"},      
                    ]
                },
            ]
            
        },
        limit=30)
    
    session['articles'] = articles
    # pprint(session)
    return redirect('/home')

@app.route('/home')
def home():
    return render_template("frontpage.html", articles=session['articles'], items_per_row=3)

@app.route('/article/<article_id>', methods=['GET', 'POST'])
def read_article(article_id: str):
    article = read_one({'_id':ObjectId(article_id)})
    return render_template('article.html', article = article)