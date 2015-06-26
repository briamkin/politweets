#------------- IMPORT MODULES ---------------#
import flask
from flask import render_template
from county_geo import *
from twitter_functions import *

# Initialize the app
app = flask.Flask(__name__)

#------------------ ROUTES ------------------#
@app.route("/")
def home():
    """
    Return home page with Top Candidates Visualization
    """
    return render_template('index.html')

@app.route("/cloud/<candidate>/<date>")
def cloud(candidate=None,date=None):
    """
    Return word cloud page based on candidate and date
    """
    return render_template('cloud.html', candidate=candidate, date=date)

@app.route("/wordcloud", methods=["POST"])
def wordcloud():
    """
    When A POST request is made to this uri, return bag of words data for given params
    """
    data = flask.request.json
    topics = { 'data' : get_topic_dictionary(data['candidate'],data['date']) }
    return flask.jsonify(topics)

@app.route("/topic/<candidate>/<date>")
def topic(candidate=None,date=None):
    """
    Return topic page based on candidate and date
    """
    return render_template('topics.html', candidate=candidate, date=date)

@app.route("/topics", methods=["POST"])
def topics():
    """
    When A POST request is made to this uri, return lda topic data for given params
    """
    data = flask.request.json
    topics = { 'data' : get_topics(data['candidate'],data['date']) }
    return flask.jsonify(topics)

@app.route("/tweets", methods=["POST"])
def tweets():
    """
    When A POST request is made to this uri, return tweets in last time period
    """
    data = flask.request.json
    tweets = return_tweets(data['hrs'], data['search'])
    return flask.jsonify(tweets)

@app.route("/candidates", methods=["POST"])
def candidates():
    """
    When A POST request is made to this uri, return all candidate data in the given time period
    """
    data = flask.request.json
    tweets = { 'data': get_all_candidates_js_objects(10, data['group'], data['individual']) }
    return flask.jsonify(tweets)

@app.route("/candidate/<name>")
def candidate(name=None):
    """
    Return individual candidate page
    """
    return render_template('candidate.html', name=candidate_slugs[name])

@app.route("/map/<candidate>/<date>")
def map(candidate=None,date=None):
    """
    Create a TSV for specified candidate and date if it doesn't already exist (update if same day)
    """
    create_map_tsv(date, candidate, 1);
    return render_template('map.html')

@app.route("/stream", methods=["POST"])
def stream():
    """
    When A POST request is made to this uri, return all tweets from the last 10 seconds.
    """
    tweets = { 'tweets' : return_last_tweets() }
    return flask.jsonify(tweets)

#--------- RUN WEB APP SERVER ------------#
app.run(host='0.0.0.0', port=5000, debug=True)
