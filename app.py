from flask import Flask, session, render_template, request, redirect, url_for
from utils import read_db
from pprint import pprint

app = Flask('app')

@app.route('/', methods=['GET', 'POST'])
def index():
    articles = read_db(limit=40)
    return render_template("frontpage.html", articles=articles)