from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import cnfg
import json
from geo import *
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
# from textblob import TextBlob
from pymongo import MongoClient
import time
import logging
import logging.handlers
import datetime
import os.path
from bson.json_util import dumps

# setup logging
LEVEL = logging.DEBUG
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
config = cnfg.load(".twitter_config")
logger = logging.getLogger(__name__)
logger.setLevel(LEVEL)
handler = logging.handlers.RotatingFileHandler('logs/debug.log', maxBytes=2000000, backupCount=20)
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
    file_name = str(twitter_time.year) + str(twitter_time.month) + str(twitter_time.day - 1) + "_tweets.json"
    try:
        if (not os.path.isfile("mongo_backups/" + file_name)):
            if (twitter_time.year == current_time.year and
                twitter_time.month == current_time.month and
                twitter_time.day == current_time.day and
                twitter_time.hour == current_time.hour and
                twitter_time.minute == current_time.minute):

                end = current_time - datetime.timedelta(1)
                start = current_time - datetime.timedelta(2)
                end_time = int(end.strftime("%s")) * 1000
                start_time = int(start.strftime("%s")) * 1000
                tweets = mongo_client.fletcher.tweets
                backup = tweets.aggregate([
                            {"$match" :
                                 {"timestamp_ms":
                                    {"$gte" : start_time,"$lt" : end_time}
                                 }
                            },
                        ])
                backup_json = dumps(backup)
                with open("mongo_backups/" + file_name, 'w') as f:
                    json.dump(backup_json, f)
        else:
            pass
    except Exception:
        logger.exception("Error creating backup")
        pass


class StdOutListener(StreamListener):

    def on_data(self, data):
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
                point = (coordinate[0], coordinate[1])
                location = find_county(point,1)
                if location != None:
                    tweet_data = {}
                    tweet_data['fips'] = location[0]
                    tweet_data['county'] = str(location[1])
                    tweet_data['state'] = str(location[2])
                    tweet_data['coordinates'] = coordinate
                    loc_name = str(location[1]) + ", " + str(location[2])
                    try:
                        tweet_data['text'] = tweet['text'].encode('utf-8')
                        tweet_data['sentiment'] = vaderSentiment(tweet_data['text'])
                    except Exception:
                        logger.exception("Error adding text")
                        tweet_data['text'] = None
                    try:
                        tweet_data['retweet_count'] = tweet['retweet_count']
                    except Exception:
                        logger.exception("Error adding retweet_count")
                        tweet_data['retweet_count'] = None
                    try:
                        tweet_data['retweeted'] = tweet['retweeted']
                    except Exception:
                        logger.exception("Error adding retweeted")
                        tweet_data['retweeted'] = None
                    try:
                        tweet_data['timestamp_ms'] = int(float(tweet['timestamp_ms']))
                        try:
                            backup_mongo_daily(tweet_data['timestamp_ms'], client)
                        except Exception:
                            logger.exception("Daily backup error")
                    except Exception:
                        logger.exception("Missing tweet timestamp")
                        tweet_data['timestamp_ms'] = None
                    try:
                        tweet_data['hashtags'] = tweet['entities']['hashtags']
                    except Exception:
                        logger.exception("Error adding hashtags")
                        tweet_data['hashtags'] = None
                    try:
                        tweet_data['profile_img'] = tweet['user']['profile_image_url']
                    except Exception:
                        logger.exception("Error adding profile_image_url")
                        tweet_data['profile_img'] = None
                    try:
                        tweet_data['screen_name'] = tweet['user']['screen_name']
                    except Exception:
                        logger.exception("Error adding screen_name")
                        tweet_data['screen_name'] = None
                    try:
                        tweet_data['friends_count'] = tweet['user']['friends_count']
                    except Exception:
                        logger.exception("Error adding friends_count")
                        tweet_data['friends_count'] = None
                    try:
                        tweets.insert_one(tweet_data)
                        print loc_name, point
                        print tweet_data['text'], "\n"
                        print tweet_data['sentiment']
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
            logger.exception("Stream error. Increasing try time to: " + str(delay) + " seconds")
            time.sleep(delay)
            delay *= 2
            stream.filter(locations=all_us)
