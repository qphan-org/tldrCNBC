from flask import Flask, session, render_template, request, redirect, url_for, flash
from utils import read_db, read_one, get_count
from pprint import pprint
from bson.objectid import ObjectId
import json

app = Flask('app')
app.secret_key = "leo-phan"

@app.route('/', methods=['GET', 'POST'])
@
def index():
    session.clear()
    session['articles'] = read_db()
    session['count']    = get_count()
    return redirect(url_for('home'))

@app.route('/home')
@app.route('/home/<int:idx>')
@app.route('/home/<text>')
@app.route(url:='/home/<text>/<idx>')
def home(text=None, idx: int=1):
    print(request.full_path)
    page_url = '/'.join(request.full_path.strip('?').split('/')[:3 if text else 2])
    print('page_url:',page_url)
    print('idx:',idx)
    return render_template(
        "home.html", 
        articles=session['articles'], 
        doc_count = session['count'], 
        items_per_row=4, 
        active_idx = idx,
        limit = 32,
        page_url = page_url,
    )

@app.route('/article/<article_id>', methods=['GET', 'POST'])
def read_article(article_id: str):
    article = read_one({'_id':ObjectId(article_id)})
    return render_template('article.html', article = article)

@app.route('/ticker/<ticker>', methods=['GET', 'POST'])
def search_ticker(ticker: str):
    session.clear()
    query = {'tickers':ticker}
    session['articles'] = read_db(query)
    session['count']    = get_count(query)
    return redirect(url_for('home', text=ticker))

@app.route('/keyword/<keyword>', methods=['GET', 'POST'])
@app.route('/keyword/<keyword>/<idx>', methods=['GET', 'POST'])
def search_keyword(keyword: str, idx: int = 1):
    session.clear()
    query = {'keywords': keyword}
    session['articles'] = read_db(query, skip=idx-1)
    session['count']    = get_count(query)
    return redirect(url_for('home', text=keyword, idx = idx))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_input = request.form["search"].upper().strip()
        
        if not search_input:
            return redirect(url_for('index'))
        
        # assume search input is a ticker
        results = read_db({'tickers':search_input})
        count   = get_count({'tickers':search_input})
        
        # if search results is empty, then search it in keyword
        if len(results) == 0:
            query = {
                    'keywords': {
                        '$regex': search_input,
                        '$options': 'i',
                    }
                }
            search_input = search_input.lower()
            results = read_db(query)
            count   = get_count(query)
            
        # need a check whether results is empty or not            
        session.clear()
        session['articles'] = results
        session['count']    = count
        return redirect(url_for('home', text=search_input))
    
    return redirect(url_for('home'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    flash('Created by Quân (Leo) Phan')
    return render_template('about.html')