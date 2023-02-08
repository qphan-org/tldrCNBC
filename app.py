from flask import Flask, session, render_template, request, redirect, url_for, flash
from utils import find_all_local, find_one_local, count_local, if_exists_local
from bson.objectid import ObjectId
import math
import json
import re

app = Flask(__name__)
app.secret_key = json.load(open("config.json", "r"))['FLASK_SECRET_KEY']
cache = dict()

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:idx>')
def index(idx: int=1):
    if cache.get('last_request') != f'/{idx}':
        if not validate_idx(idx):
            return redirect(url_for('index', idx=cache['active_idx']))
        cache.clear()
        cache['articles'] = find_all_local(skip=idx-1)
        cache['count']    = count_local()
        cache['last_request'] = f'/{idx}'
        cache['active_idx'] = idx
        
    return render_homepage()

@app.route('/article/<article_id>', methods=['GET', 'POST'])
def read_article(article_id: str):
    article = find_one_local({'_id':ObjectId(article_id)})
    return render_template('article.html', article = article)

@app.route('/ticker/<ticker>', methods=['GET', 'POST'])
@app.route('/ticker/<ticker>/<int:idx>', methods=['GET', 'POST'])
def search_ticker(ticker: str, idx: int = 1):
    query = {'tickers':ticker}
    if cache.get('last_request') != f'/ticker/{ticker}/{idx}':
        if not validate_idx(idx):
            return redirect(url_for('search_keyword', ticker=ticker, idx=cache['active_idx']))
        cache.clear()
        cache['articles'] = find_all_local(query, skip=idx-1)
        cache['count']    = count_local(query)
        cache['last_request'] = f'/ticker/{ticker}/{idx}'
        cache['active_idx'] = idx

    return render_homepage(f'/ticker/{ticker}')

@app.route('/keyword/<keyword>', methods=['GET', 'POST'])
@app.route('/keyword/<keyword>/<int:idx>', methods=['GET', 'POST'])
def search_keyword(keyword: str, idx: int = 1):
    keyword = re.sub(r'[^A-Za-z0-9 ]+', '', keyword).lower()
    query = {
        'keywords': {
            '$regex': keyword,
            '$options': 'i',
        }
    }
    if cache.get('last_request') != f'/keyword/{keyword}/{idx}':
        if not validate_idx(idx):
            return redirect(url_for('search_keyword', keyword=keyword, idx=cache['active_idx']))
        cache.clear()
        cache['articles'] = find_all_local(query, skip=idx-1)
        cache['count']    = count_local(query)
        cache['last_request'] = f'/keyword/{keyword}/{idx}'
        cache['active_idx'] = idx
    
    return render_homepage(page_url=f'/keyword/{keyword}')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_input = request.form["search"].strip()
        if not search_input:
            return redirect(url_for('index'))
        
        # assume search input is a ticker
        if if_exists_local({'tickers':search_input.upper()}):
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
        articles        = cache['articles'], 
        doc_count       = cache['count'], 
        active_idx      = cache['active_idx'],
        page_url        = page_url,
        items_per_row   = 4, 
        limit           = 32,
    )
    
def validate_idx(idx: int):
    if idx == 1:
        return True
    
    if idx <= 0:
        return False
    
    if (count := cache.get('count')) != None:
        return idx <= math.ceil(count/32)
