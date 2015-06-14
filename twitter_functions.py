from __future__ import division
import flask
from pymongo import MongoClient
import time
from county_geo import *
from twitter_functions import *
import math
from datetime import date

def return_tweets(day, search_terms="", all_results=0):
    today_epoch = int(date.today().strftime('%s'))
    start_time = (today_epoch - (day*86400))*1000
    end_time = ((start_time + 86400)*1000)-1
    if all_results==1:
        start_time = 0
        end_time = (today_epoch+86400)*1000
    client = MongoClient()
    db = client.fletcher.tweets
    tweets = {}
    if search_terms != "":
        query = db.aggregate([
            {"$match":{"$text":{"$search":search_terms}}},
            {"$match":{"timestamp_ms":{"$gte":start_time,"$lt":end_time}}}])
    else:
        query = db.aggregate([
            {"$match":{"timestamp_ms":{"$gte":start_time,"$lt":end_time}}}])
    for tweet in query:
        fips = tweet['fips']
        if fips in tweets:
            tweets[fips]['volume'] += 1
            try:
                tweets[fips]['sentiment'] += tweet['sentiment']['compound']
            except:
                pass
        else:
            tweets[fips] = {}
            tweets[fips]['volume'] = 1
            try:
                tweets[fips]['sentiment'] = tweet['sentiment']['compound']
            except:
                tweets[fips]['sentiment'] = 0
    for x in tweets:
        tweets[x]['sentiment'] = tweets[x]['sentiment']/tweets[x]['volume']

    return tweets

def tweet_booststrapper(dict, n=0):
    bootstrap_dict = {}
    for key in all_fips:
        try:
            volume = dict[key]['volume']
            sentiment = dict[key]['sentiment']
        except:
            volume = 0
            sentiment = None
        if volume < 100:
            new_sent, new_vol, weight, new_mult = 0, 0, 10, 0
            for county in nearest_counties[key]:
                try:
                    vol = dict[county]['volume']*weight
                    new_vol += vol
                    new_sent += dict[county]['sentiment']*multiplier
                    new_mult += multiplier
                except:
                    pass
                weight -= 1
            new_vol = (volume*(volume/100))+((new_vol/55)*((100-volume)/100))
            if new_mult > 0:
                new_sent = (volume*(volume/100))+((new_sent/new_mult)*((100-volume)/100))
            else:
                new_sent = sentiment
        else:
            new_vol = volume
            new_sent = sentiment
        bootstrap_dict[key] = {}
        bootstrap_dict[key]['volume'] = new_vol
        bootstrap_dict[key]['sentiment'] = new_sent
    if n > 0:
        n -= 1
        return tweet_booststrapper(bootstrap_dict, n)
    return bootstrap_dict


def get_all_candidates(time=0, n=0, all_results=0):
    candidate_search = { "Lincoln Chafee" : "lincolnchafee chafee teamchafee teamlincolnchafee chafee2016 lincolnchafee2016 chafeeforpresident chafee4president",  "Hillary Clinton" : "hillaryclinton hillary teamhillary teamclinton teamhillaryclinton hillary2016 clinton2016 hillaryclinton2016 hillaryforamerica hillary4america hillaryforpresident hillary4president",  "Martin O'Malley" : "governoromalley martinomalley teamomalley teammartinomalley omalley2016 martinomalley2016 omalley4president omalleyforpresident",  "Bernie Sanders" : "berniesanders sensanders teambernie teamberniesanders bernie2016 sanders2016 berniesanders2016 sanders4president sandersforpresident bernie4president bernieforpresident berniesanderse4president berniesanderseforpresident",  "Ben Carson" : "realbencarson bencarson drbencarson teamcarson teambencarson bencarson2016 carson2016 carson4president carsonforpresident bencarson4president bencarsonforpresident",  "Ted Cruz" : "tedcruz sentedcruz teamcruz teamtedcruz tedcruz2016 cruzcrew cruz4president cruzforpresident tedcruz4president tedcruzforpresident",  "Carly Fiorina" : "carlyfiorina fiorina teamcarly teamfiorina teamcarlyfiorina carly2016 carly4president carlyforpresident carlyfiorina4president carlyfiorinaforpresident fiorina4president fiorinaforpresident",  "Lindsey Graham" : "linseygrahamsc lindseygraham grahamblog senlindseygraham teamgraham teamlindseygraham graham2016 lindseygraham2016 graham4president grahamforpresident lindseygraham4president lindseygrahamforpresident",  "George Pataki" : "governorpataki govpataki pataki georgepataki pataki4president patakiforpresident georgepataki4president georgepatakiforpresident teampataki",  "Rand Paul" : "randpaul drrandpaul senatorrandpaul teamrand teamrandpaul randpaul2016 rand2016 standwithrand rand4president randforpresident paul4president paulforpresident randpaul4president randpaulforpresident",  "Rick Perry" : "governorperry rickperry teamrickperry perry2016 rickperry2016 perry4president perryforpresident rickperry4president rickperryforpresident",  "Marco Rubio" : "marcorubio rubio2016 marcorubio2016 teammarco teammarcorubio marco4president marcoforpresident rubio4president rubioforpresident marcorubio4president marcorubioforpresident",  "Rick Santorum" : "ricksantorum santorum2016 teamsantorum teamricksantorum santorum4president santorumforpresident ricksantorum4president ricksantorumforpresident",  "Mike Huckabee" : "govmikehuckabee mikehuckabee teamhuckabee teammikehuckabee huckabee2016 mikehuckabee2016 huckaboom huckabee4president huckabeeforpresident mikehuckabee4president mikehuckabeeforpresident",  "Jeb Bush" : "jebbush  teamjeb teamjebbush jeb2016 bush2016 jebbush2016 jeb jeb4president jebforpresident jebbush4president jebbushforpresident",  "Scott Walker" : "scottwalker teamscottwalker scottwalker2016 walker4president walkerforpresident scottwalker4president scottwalkerforpresident" }
    candidate_tweets = {}
    candidate_totals = {}
    for key in candidate_search:
        total_volume = 0
        total_sentiment = 0
        total_sent_vol = 0
        search_terms = candidate_search[key]
        tweets = return_tweets(time, search_terms, all_results)
        boosted_tweets = tweet_booststrapper(tweets,n)
        candidate_tweets[key] = boosted_tweets
        for county in boosted_tweets:
            county_volume = boosted_tweets[county]['volume']
            county_sentiment = boosted_tweets[county]['sentiment']
            total_volume += county_volume
            if county_sentiment != None:
                total_sentiment += (county_volume*county_sentiment)
                total_sent_vol += county_volume
        candidate_totals[key] = {}
        try:
            candidate_totals[key]['volume'] = total_volume
            candidate_totals[key]['sentiment'] = total_sentiment/total_sent_vol
        except:
            candidate_totals[key]['volume'] = 0
            candidate_totals[key]['sentiment'] = 0
    all_data = {"total" : candidate_totals, "county" : candidate_tweets}
    return all_data

def get_all_candidates_daily(time=1):
    day_array = {}
    for x in range(time):
        day_array[x] = get_all_candidates(x)
    return day_array
