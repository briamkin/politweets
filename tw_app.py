from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import cnfg
import json
from geo import *
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
from textblob import TextBlob
from pymongo import MongoClient
import time
import logging
import logging.handlers
import datetime
import os.path

# setup logging
LEVEL = logging.DEBUG
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
config = cnfg.load(".twitter_config")
logger = logging.getLogger(__name__)
logger.setLevel(LEVEL)
handler = logging.handlers.RotatingFileHandler('debug.log', maxBytes=2000000, backupCount=20)
handler.setLevel(LEVEL)
handler.setFormatter(formatter)
logger.addHandler(handler)

# get Twitter auth
access_token = config['access_token']
access_token_secret = config['access_token_secret']
consumer_key = config['consumer_key']
consumer_secret = config['consumer_secret']

def backup_mongo_daily(timestamp, mongo_client):
    twitter_time = datetime.datetime.fromtimestamp(timestamp/1000)
    current_time = datetime.datetime.today()
    file_name = str(timestamp.year) + str(timestamp.month) + str(timestamp.day - 1) + "_tweets.json"
    if (not os.path.isfile("mongo_backups/" + file_name)):
        if (twitter_time.year == current_time.year and
            twitter_time.month == current_time.month and
            twitter_time.day == current_time.day and
            twitter_time.hour == current_time.hour and
            twitter_time.minute == current_time.minute):

            end = current_time - datetime.timedelta(1)
            start = current_time - datetime.timedelta(2)
            end_time = int(end.strftime("%s"))
            start_time = int(start.strftime("%s"))
            tweets = mongo_client.fletcher.tweets


class StdOutListener(StreamListener):

    def on_data(self, data):
        fields = ['created_at', 'id', 'text', 'source', 'user', 'geo', 'entities', 'possibly_sensitive', 'filter_level', 'retweet_count', 'retweeted']
        client = MongoClient()
        tweets = client.fletcher.tweets
        tweet = json.loads(data)
        try:
            try:
                coordinate = tweet['geo']['coordinates']
            except Exception:
                logger.exception("Trying 2nd coordinates field")
                coordinate = tweet['coordinates']
            if coordinate != None:
                point = (coordinate['coordinates'][1], coordinate['coordinates'][0])
                location = find_county(point,1)
                if location != None:
                    tweet_data = {}
                    for field in fields:
                        if field == 'text':
                            try:
                                tweet_data['text'] = tweet['text'].encode('utf-8')
                            except Exception:
                                logger.exception("No tweet text data")
                                tweet_data['text'] = None
                        else:
                            try:
                                tweet_data[field] = tweet[field]
                            except Exception:
                                logger.exception("Missing tweet field data")
                                tweet_data[field] = None
                    tweet_data['fips'] = location[0]
                    loc_name = str(location[1]) + ", " + str(location[2])
                    try:
                        tweet_data['timestamp_ms'] = int(float(tweet['timestamp_ms']))
                    except Exception:
                        logger.exception("Missing tweet timestamp")
                        tweet_data['timestamp_ms'] = None
                    try:
                        tweets.insert_one(tweet_data)
                        print loc_name, point
                        print tweet_data['text'], "\n"
                    except Exception:
                        logger.exception("Error inserting into Mongo")

                    return True
        except Exception:
            logger.exception("Error getting tweet")
            pass

    def on_error(self, status):
        print "error", status


if __name__ == '__main__':

    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    delay = 8
    all_us = [-169.90,52.72,-130.53,72.40,-160.6,18.7,-154.5,22.3,-124.90,23.92,-66.37,50.08]
    while True:
        try:
            stream.filter(locations=all_us)
            delay = 8
        except Exception:
            logger.exception("Stream error. Increasing try time to: " + delay + " seconds")
            time.sleep(delay)
            delay *= 2
            stream.filter(locations=all_us)
