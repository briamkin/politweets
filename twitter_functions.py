from __future__ import division
import flask
from pymongo import MongoClient
import time
from county_geo import *
from twitter_functions import *
import math

def return_tweets(hours, search_terms=""):
    current_epoch_time = int(time.time())
    client = MongoClient()
    db = client.fletcher.tweets
    tweets = {}
    seconds = hours * 3600
    min_time = (current_epoch_time - seconds) * 1000
    if search_terms != "":
        query = db.aggregate([
            {"$match":{"$text":{"$search":search_terms}}},
            {"$match":{"timestamp_ms":{"$gte":min_time}}}])
    else:
        query = db.aggregate([
            {"$match":{"timestamp_ms":{"$gte":min_time}}}])
    for tweet in query:
        fips = tweet['fips']
        if fips in tweets:
            # tweets[fips] += (100000/fips_pop[fips])
            tweets[fips]['volume'] += 1
            try:
                tweets[fips]['sentiment'] += tweet['sentiment']['compound']
            except:
                pass
        else:
            # tweets[fips] = (100000/fips_pop[fips])
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
    bs_dict = {}
    for key in all_fips:
        try:
            volume = dict[key]['volume']
            sentiment = dict[key]['sentiment']
        except:
            volume = 0
            sentiment = None
        new_vol = 0
        sent_vol = 0
        if sentiment != None:
            new_sent = sentiment*15*volume
        else:
            new_sent = 0
        multiplier = 10
        for county in nearest_counties[key]:
            try:
                new_vol += (dict[county]['volume']*multiplier)
                new_sent += (dict[county]['sentiment']*multiplier*dict[county]['volume'])
                sent_vol += multiplier
            except:
                pass
            multiplier -= 1
        if volume > 0:
            if volume < 100:
                fraction = 0.95*math.log(volume)/2
                new_vol= (volume*fraction)+((new_vol/55)*(1-fraction))
                new_sent = (sentiment*fraction)+((new_sent/((volume*15)+sent_vol))*(1-fraction))
            else:
                new_vol = (volume*0.95)+((new_vol/55)*0.05)
                new_sent = (sentiment*0.95)+((new_sent/((volume*15)+sent_vol))*0.05)
        else:
            new_vol = new_vol/55
            denom = (volume*15)+sent_vol
            if denom != 0:
                new_sent = new_sent/denom
            else:
                new_sent = None
        bs_dict[key] = {}
        bs_dict[key]['volume'] = new_vol
        bs_dict[key]['sentiment'] = new_sent
    if n > 0:
        n -= 1
        return tweet_booststrapper(bs_dict, n)
    return bs_dict


def get_all_candidates(time, n=0):
    candidate_search = { "Lincoln Chafee" : "lincolnchafee chafee teamchafee teamlincolnchafee chafee2016 lincolnchafee2016 chafeeforpresident chafee4president",  "Hillary Clinton" : "hillaryclinton hillary teamhillary teamclinton teamhillaryclinton hillary2016 clinton2016 hillaryclinton2016 hillaryforamerica hillary4america hillaryforpresident hillary4president",  "Martin O'Malley" : "governoromalley martinomalley teamomalley teammartinomalley omalley2016 martinomalley2016 omalley4president omalleyforpresident",  "Bernie Sanders" : "berniesanders sensanders teambernie teamberniesanders bernie2016 sanders2016 berniesanders2016 sanders4president sandersforpresident bernie4president bernieforpresident berniesanderse4president berniesanderseforpresident",  "Ben Carson" : "realbencarson bencarson drbencarson teamcarson teambencarson bencarson2016 carson2016 carson4president carsonforpresident bencarson4president bencarsonforpresident",  "Ted Cruz" : "tedcruz sentedcruz teamcruz teamtedcruz tedcruz2016 cruzcrew cruz4president cruzforpresident tedcruz4president tedcruzforpresident",  "Carly Fiorina" : "carlyfiorina fiorina teamcarly teamfiorina teamcarlyfiorina carly2016 carly4president carlyforpresident carlyfiorina4president carlyfiorinaforpresident fiorina4president fiorinaforpresident",  "Lindsey Graham" : "linseygrahamsc lindseygraham grahamblog senlindseygraham teamgraham teamlindseygraham graham2016 lindseygraham2016 graham4president grahamforpresident lindseygraham4president lindseygrahamforpresident",  "George Pataki" : "governorpataki govpataki pataki georgepataki pataki4president patakiforpresident georgepataki4president georgepatakiforpresident teampataki",  "Rand Paul" : "randpaul drrandpaul senatorrandpaul teamrand teamrandpaul randpaul2016 rand2016 standwithrand rand4president randforpresident paul4president paulforpresident randpaul4president randpaulforpresident",  "Rick Perry" : "governorperry rickperry teamrickperry perry2016 rickperry2016 perry4president perryforpresident rickperry4president rickperryforpresident",  "Marco Rubio" : "marcorubio rubio2016 marcorubio2016 teammarco teammarcorubio marco4president marcoforpresident rubio4president rubioforpresident marcorubio4president marcorubioforpresident",  "Rick Santorum" : "ricksantorum santorum2016 teamsantorum teamricksantorum santorum4president santorumforpresident ricksantorum4president ricksantorumforpresident",  "Mike Huckabee" : "govmikehuckabee mikehuckabee teamhuckabee teammikehuckabee huckabee2016 mikehuckabee2016 huckaboom huckabee4president huckabeeforpresident mikehuckabee4president mikehuckabeeforpresident",  "Jeb Bush" : "jebbush  teamjeb teamjebbush jeb2016 bush2016 jebbush2016 jeb jeb4president jebforpresident jebbush4president jebbushforpresident",  "Scott Walker" : "scottwalker teamscottwalker scottwalker2016 walker4president walkerforpresident scottwalker4president scottwalkerforpresident" }
    candidate_tweets = {}
    candidate_totals = {}
    for key in candidate_search:
        total_volume = 0
        total_sentiment = 0
        total_sent_vol = 0
        search_terms = candidate_search[key]
        tweets = return_tweets(time, search_terms)
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

# def return_history():
#     current_time = int(time.time())
#     five_min = (current_time - 300) * 1000
#     ten_min = (current_time - 600) * 1000
#     fifteen_min = (current_time - 900) * 1000
#     client = MongoClient()
#     db = client.fletcher.tweets
#     five_counts = {}
#     ten_counts = {}
#     fifteen_counts = {}
#     momentum = {}
#     for area in areas:
#         count = db.find({"city_area":area,"timestamp_ms":{"$gte":five_min}}).count()
#         five_counts[area] = count
#     for area in areas:
#         count = db.find({"city_area":area,"timestamp_ms":{"$gte":ten_min, "$lt":five_min}}).count()
#         ten_counts[area] = count
#     for area in areas:
#         count = db.find({"city_area":area,"timestamp_ms":{"$gte":fifteen_min, "$lt":ten_min}}).count()
#         fifteen_counts[area] = count
#     for area in areas:
#         change1 = (fifteen_counts[area]-ten_counts[area])/(fifteen_counts[area]+0.001)
#         change2 = (ten_counts[area]-five_counts[area])/(ten_counts[area]+0.001)
#         if change1 > 0 and change2 > 0:
#             if change2 > change1:
#                 momentum[area] = 6
#             else:
#                 momentum[area] = 5
#         elif change1 <= 0 and change2 <= 0:
#             if change1 < change2:
#                 momentum[area] = 3
#             else:
#                 momentum[area] = 1
#         elif change1 >= 0 and change2 <= 0:
#             momentum[area] = 2
#         elif change2 <= 0 and change2 >= 0:
#             momentum[area] = 4
#         else:
#             momentum[area] = 0
#     return momentum
