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

config = cnfg.load(".twitter_config")

#Variables that contains the user credentials to access Twitter API
access_token = config['access_token']
access_token_secret = config['access_token_secret']
consumer_key = config['consumer_key']
consumer_secret = config['consumer_secret']

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, data):
        fields = ['created_at', 'id', 'text', 'source', 'user', 'geo', 'coordinates', 'entities', 'possibly_sensitive', 'filter_level']
        client = MongoClient()
        tweets = client.fletcher.tweets
        tweet = json.loads(data)
        coordinate = tweet['coordinates']
        if coordinate != None:
            point = (coordinate['coordinates'][1], coordinate['coordinates'][0])
            location = find_location(point)
            if location != None:
                tweet_data = {}
                for field in fields:
                    try:
                        tweet_data[field] = tweet[field]
                    except:
                        tweet_data[field] = None
                tweet_data['city_area'] = location
                try:
                    tweet_data['timestamp_ms'] = int(float(tweet['timestamp_ms']))
                except:
                    tweet_data['timestamp_ms'] = None
                tweets.insert_one(tweet_data)
                print location, point
                text = tweet['text'].encode('utf-8')
                print text, "\n"
                # blob_text = TextBlob(tweet['text'])
                # print vaderSentiment(text)
                # print blob_text.sentiment
                # print
                return True

    def on_error(self, status):
        print status


if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    # stream.filter(track=['python', 'javascript', 'ruby'])
    stream.filter(locations=[-122.6,37.25,-121.75,38,-74.1,40.5,-73.6,40.9])
