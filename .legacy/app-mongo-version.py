from flask import Flask, session, render_template, request, redirect, url_for, flash
from utils import find_all_mongo, find_one_mongo, count_mongo, if_exists_mongo
from bson.objectid import ObjectId
import math
import json

app = Flask(__name__)
app.secret_key = json.load(open("config.json", "r"))['FLASK_SECRET_KEY']


@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:idx>')
def index(idx: int=1):
    if session.get('last_request') != f'/{idx}':
        if not validate_idx(idx):
            return redirect(url_for('search_keyword', idx=session['active_idx']))
        session.clear()
        session['articles'] = find_all_mongo(skip=idx-1)
        session['count']    = count_mongo()
        session['last_request'] = f'/{idx}'
        session['active_idx'] = idx
        
    return render_homepage()

@app.route('/article/<article_id>', methods=['GET', 'POST'])
def read_article(article_id: str):
    article = find_one_mongo({'_id':ObjectId(article_id)})
    return render_template('article.html', article = article)

@app.route('/ticker/<ticker>', methods=['GET', 'POST'])
@app.route('/ticker/<ticker>/<int:idx>', methods=['GET', 'POST'])
def search_ticker(ticker: str, idx: int = 1):
    query = {'tickers':ticker}
    if session.get('last_request') != f'/ticker/{ticker}/{idx}':
        if not validate_idx(idx):
            return redirect(url_for('search_keyword', ticker=ticker, idx=session['active_idx']))
        session.clear()
        session['articles'] = find_all_mongo(query, skip=idx-1)
        session['count']    = count_mongo(query)
        session['last_request'] = f'/ticker/{ticker}/{idx}'
        session['active_idx'] = idx

    return render_homepage(f'/ticker/{ticker}')

@app.route('/keyword/<keyword>', methods=['GET', 'POST'])
@app.route('/keyword/<keyword>/<int:idx>', methods=['GET', 'POST'])
def search_keyword(keyword: str, idx: int = 1):
    query = {
        'keywords': {
            '$regex': keyword,
            '$options': 'i',
        }
    }
    if session.get('last_request') != f'/keyword/{keyword}/{idx}':
        if not validate_idx(idx):
            return redirect(url_for('search_keyword', keyword=keyword, idx=session['active_idx']))
        session.clear()
        session['articles'] = find_all_mongo(query, skip=idx-1)
        session['count']    = count_mongo(query)
        session['last_request'] = f'/keyword/{keyword}/{idx}'
        session['active_idx'] = idx
    
    return render_homepage(page_url=f'/keyword/{keyword}')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_input = request.form["search"].strip()
        if not search_input:
            return redirect(url_for('index'))
        
        # assume search input is a ticker
        if if_exists_mongo({'tickers':search_input.upper()}):
            return redirect(url_for('search_ticker', ticker=search_input.upper()))
        else:
            return redirect(url_for('search_keyword', keyword=search_input.lower()))
        
    return redirect(url_for('index'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    flash('Created by Quân (Leo) Phan')
    return render_template('about.html')


""" Helper functions """

def render_homepage(page_url: str = ""):
    return render_template(
        "home.html", 
        articles        = session['articles'], 
        doc_count       = session['count'], 
        active_idx      = session['active_idx'],
        page_url        = page_url,
        items_per_row   = 4, 
        limit           = 32,
    )
    
def validate_idx(idx: int):
    if idx == 1:
        return True
    
    if idx <= 0:
        return False
    
    if (count := session['count']) != None:
        return idx <= math.ceil(count/32)
