#Import the necessary methods from tweepy library
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

config = cnfg.load(".twitter_config")

access_token = config['access_token']
access_token_secret = config['access_token_secret']
consumer_key = config['consumer_key']
consumer_secret = config['consumer_secret']

class StdOutListener(StreamListener):

    def on_data(self, data):
        fields = ['created_at', 'id', 'text', 'source', 'user', 'geo', 'coordinates', 'entities', 'possibly_sensitive', 'filter_level']
        client = MongoClient()
        tweets = client.fletcher.tweets
        tweet = json.loads(data)
        try:
            coordinate = tweet['coordinates']
            if coordinate != None:
                point = (coordinate['coordinates'][1], coordinate['coordinates'][0])
                location = find_county(point,1)
                if location != None:
                    tweet_data = {}
                    for field in fields:
                        try:
                            tweet_data[field] = tweet[field]
                        except:
                            tweet_data[field] = None
                    tweet_data['fips'] = location[0]
                    loc_name = str(location[1]) + ", " + str(location[2])
                    try:
                        tweet_data['timestamp_ms'] = int(float(tweet['timestamp_ms']))
                    except:
                        tweet_data['timestamp_ms'] = None
                    try:
                        tweets.insert_one(tweet_data)
                        print loc_name, point
                        text = tweet['text'].encode('utf-8')
                        print text, "\n"
                    except:
                        print "error"
                    # blob_text = TextBlob(tweet['text'])
                    # print vaderSentiment(text)
                    # print blob_text.sentiment
                    # print
                    return True
        except:
            pass

    def on_error(self, status):
        print "error",status


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
        except:
            print "Error. Trying again"
            time.sleep(delay)
            delay *= 2
            stream.filter(locations=all_us)
