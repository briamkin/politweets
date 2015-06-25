#------------- IMPORT MODULES ---------------#

from __future__ import division
import flask
from flask import render_template
from pymongo import MongoClient
import time
from county_geo import *
from twitter_functions import *
import math
from datetime import date, timedelta, datetime
import re
from collections import defaultdict
from gensim.models.ldamodel import LdaModel
from gensim import corpora, models, similarities
import os
#---------- URLS AND WEB PAGES -------------#

# Initialize the app
app = flask.Flask(__name__)

# Homepage
@app.route("/")
def home():
    """
    Homepage: serve our visualization page, awesome.html
    """
    return render_template('index.html')

@app.route("/cloud/<candidate>/<date>")
def cloud(candidate=None,date=None):
    """
    When A POST request is made to this uri, return all candidate data in the last time period.
    """
    return render_template('cloud.html', candidate=candidate, date=date)

@app.route("/wordcloud", methods=["POST"])
def wordcloud():
    """
    When A POST request is made to this uri, return the momentum.
    """
    data = flask.request.json
    topics = { 'data' : get_topic_dictionary(data['candidate'],data['date']) }
    return flask.jsonify(topics)

@app.route("/topic/<candidate>/<date>")
def topic(candidate=None,date=None):
    """
    When A POST request is made to this uri, return all candidate data in the last time period.
    """
    return render_template('topics.html', candidate=candidate, date=date)

@app.route("/topics", methods=["POST"])
def topics():
    """
    When A POST request is made to this uri, return the momentum.
    """
    data = flask.request.json
    topics = { 'data' : get_topics(data['candidate'],data['date']) }
    return flask.jsonify(topics)

@app.route("/tweets", methods=["POST"])
def tweets():
    """
    When A POST request is made to this uri, return tweets in the last time period.
    """
    data = flask.request.json
    tweets = return_tweets(data['hrs'], data['search'])
    return flask.jsonify(tweets)

@app.route("/candidates", methods=["POST"])
def candidates():
    """
    When A POST request is made to this uri, return all candidate data in the last time period.
    """
    data = flask.request.json
    tweets = { 'data': get_all_candidates_js_objects(10, data['group'], data['individual']) }
    return flask.jsonify(tweets)

@app.route("/candidate/<name>")
def candidate(name=None):
    """
    When A POST request is made to this uri, return all candidate data in the last time period.
    """
    return render_template('candidate.html', name=candidate_slugs[name])

@app.route("/map/<candidate>/<date>")
def map(candidate=None,date=None):
    """
    When A POST request is made to this uri, return all candidate data in the last time period.
    """
    create_map_tsv(date, candidate);
    return render_template('map.html')

@app.route("/stream", methods=["POST"])
def stream():
    """
    When A POST request is made to this uri, return all tweets from the last 10 seconds.
    """
    tweets = { 'tweets' : return_last_tweets() }
    return flask.jsonify(tweets)

if __name__ == '__main__':
    app.run(debug=True)
#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
app.run(host='0.0.0.0', port=5000)
