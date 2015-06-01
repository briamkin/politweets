from __future__ import division
import flask
from pymongo import MongoClient
import time
from county_geo import county_fips, all_fips

#---------- BUILT MOMENTUM MODEL ----------------#

def return_tweets():
    current_time = int(time.time())
    client = MongoClient()
    db = client.fletcher.tweets
    tweets = {}
    minute = (current_time - 120) * 1000
    for num in fips:
        query_tweets = []
        query = db.find({"city_area":num,"timestamp_ms":{"$gte":minute}})
        for tweet in query:
            query_tweets.append([tweet['text'],tweet['timestamp_ms'],tweet['user']['screen_name'],tweet['coordinates']['coordinates']])
        tweets[area] = query_tweets
    return tweets

def return_momentum():
    current_time = int(time.time())
    five_min = (current_time - 300) * 1000
    ten_min = (current_time - 600) * 1000
    fifteen_min = (current_time - 900) * 1000
    client = MongoClient()
    db = client.fletcher.tweets
    five_counts = {}
    ten_counts = {}
    fifteen_counts = {}
    momentum = {}
    for area in areas:
        count = db.find({"city_area":area,"timestamp_ms":{"$gte":five_min}}).count()
        five_counts[area] = count
    for area in areas:
        count = db.find({"city_area":area,"timestamp_ms":{"$gte":ten_min, "$lt":five_min}}).count()
        ten_counts[area] = count
    for area in areas:
        count = db.find({"city_area":area,"timestamp_ms":{"$gte":fifteen_min, "$lt":ten_min}}).count()
        fifteen_counts[area] = count
    for area in areas:
        change1 = (fifteen_counts[area]-ten_counts[area])/(fifteen_counts[area]+0.001)
        change2 = (ten_counts[area]-five_counts[area])/(ten_counts[area]+0.001)
        if change1 > 0 and change2 > 0:
            if change2 > change1:
                momentum[area] = 6
            else:
                momentum[area] = 5
        elif change1 <= 0 and change2 <= 0:
            if change1 < change2:
                momentum[area] = 3
            else:
                momentum[area] = 1
        elif change1 >= 0 and change2 <= 0:
            momentum[area] = 2
        elif change2 <= 0 and change2 >= 0:
            momentum[area] = 4
        else:
            momentum[area] = 0
    return momentum

#---------- URLS AND WEB PAGES -------------#

# Initialize the app
app = flask.Flask(__name__)

# Homepage
@app.route("/")
def home():
    """
    Homepage: serve our visualization page, awesome.html
    """
    with open("index.html", 'r') as file:
        return file.read()

# Get an example and return it's score from the predictor model
@app.route("/momentum", methods=["POST"])
def momentum():
    """
    When A POST request is made to this uri, return the momentum.
    """

    # Put the result in a nice dict so we can send it as json
    # results = find_momentum()
    results = return_momentum()
    return flask.jsonify(results)

@app.route("/tweets", methods=["POST"])
def tweets():
    """
    When A POST request is made to this uri, return tweets in the last minute.
    """
    results = return_tweets()
    return flask.jsonify(results)

#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
app.run(host='0.0.0.0', port=5000)
