from __future__ import division
import flask
from pymongo import MongoClient
import time
from county_geo import *
from twitter_functions import *
import math
from datetime import date, timedelta, datetime
import re
import os
from collections import defaultdict
from gensim.models.ldamodel import LdaModel
from gensim import corpora, models, similarities
from operator import itemgetter

candidate_slugs = {  "lincolnchafee" : "Lincoln Chafee", "hillaryclinton" : "Hillary Clinton", "martinomalley" : "Martin O'Malley", "berniesanders" : "Bernie Sanders", "bencarson" : "Ben Carson", "tedcruz" : "Ted Cruz", "carlyfiorina" : "Carly Fiorina", "lindseygraham" : "Lindsey Graham", "georgepataki" : "George Pataki", "randpaul" : "Rand Paul", "rickperry" : "Rick Perry", "marcorubio" : "Marco Rubio", "ricksantorum" : "Rick Santorum", "mikehucakbee" : "Mike Huckabee", "jebbush" : "Jeb Bush", "scottwalker" : "Scott Walker", "donaldtrump" : "Donald Trump" }

all_candidates = ["Lincoln Chafee", "Hillary Clinton", "Martin O'Malley", "Bernie Sanders", "Ben Carson", "Ted Cruz", "Carly Fiorina", "Lindsey Graham", "George Pataki", "Rand Paul", "Rick Perry", "Marco Rubio", "Rick Santorum", "Mike Huckabee", "Jeb Bush", "Scott Walker", "Donald Trump"]

top_candidates = ["Hillary Clinton", "Bernie Sanders", "Ben Carson", "Ted Cruz", "Carly Fiorina", "Rand Paul", "Jeb Bush", "Donald Trump"]

top_democrats = ["Lincoln Chafee", "Hillary Clinton", "Martin O'Malley", "Bernie Sanders"]

top_republicans = ["Donald Trump", "Jeb Bush", "Carly Fiorina", "Jeb Bush", "Rick Santorum", "Rand Paul", "Ted Cruz"]

candidate_lists = { "top" : top_candidates, "rep" : top_republicans, "dem" : top_democrats, "all" : all_candidates }

candidate_search = { "Lincoln Chafee" : "lincolnchafee chafee teamchafee teamlincolnchafee chafee2016 lincolnchafee2016 chafeeforpresident chafee4president",  "Hillary Clinton" : "hillaryclinton hillary teamhillary teamclinton teamhillaryclinton hillary2016 clinton2016 hillaryclinton2016 hillaryforamerica hillary4america hillaryforpresident hillary4president",  "Martin O'Malley" : "governoromalley martinomalley teamomalley teammartinomalley omalley2016 martinomalley2016 omalley4president omalleyforpresident",  "Bernie Sanders" : "berniesanders sensanders teambernie teamberniesanders bernie2016 sanders2016 berniesanders2016 sanders4president sandersforpresident bernie4president bernieforpresident berniesanderse4president berniesanderseforpresident",  "Ben Carson" : "realbencarson bencarson drbencarson teamcarson teambencarson bencarson2016 carson2016 carson4president carsonforpresident bencarson4president bencarsonforpresident",  "Ted Cruz" : "tedcruz sentedcruz teamcruz teamtedcruz tedcruz2016 cruzcrew cruz4president cruzforpresident tedcruz4president tedcruzforpresident",  "Carly Fiorina" : "carlyfiorina fiorina teamcarly teamfiorina teamcarlyfiorina carly2016 carly4president carlyforpresident carlyfiorina4president carlyfiorinaforpresident fiorina4president fiorinaforpresident",  "Lindsey Graham" : "linseygrahamsc lindseygraham grahamblog senlindseygraham teamgraham teamlindseygraham graham2016 lindseygraham2016 graham4president grahamforpresident lindseygraham4president lindseygrahamforpresident",  "George Pataki" : "governorpataki govpataki pataki georgepataki pataki4president patakiforpresident georgepataki4president georgepatakiforpresident teampataki",  "Rand Paul" : "randpaul drrandpaul senatorrandpaul teamrand teamrandpaul randpaul2016 rand2016 standwithrand rand4president randforpresident paul4president paulforpresident randpaul4president randpaulforpresident",  "Rick Perry" : "governorperry rickperry teamrickperry perry2016 rickperry2016 perry4president perryforpresident rickperry4president rickperryforpresident",  "Marco Rubio" : "marcorubio rubio2016 marcorubio2016 teammarco teammarcorubio marco4president marcoforpresident rubio4president rubioforpresident marcorubio4president marcorubioforpresident",  "Rick Santorum" : "ricksantorum santorum2016 teamsantorum teamricksantorum santorum4president santorumforpresident ricksantorum4president ricksantorumforpresident",  "Mike Huckabee" : "govmikehuckabee mikehuckabee teamhuckabee teammikehuckabee huckabee2016 mikehuckabee2016 huckaboom huckabee4president huckabeeforpresident mikehuckabee4president mikehuckabeeforpresident",  "Jeb Bush" : "jebbush  teamjeb teamjebbush jeb2016 bush2016 jebbush2016 jeb jeb4president jebforpresident jebbush4president jebbushforpresident",  "Scott Walker" : "scottwalker teamscottwalker scottwalker2016 walker4president walkerforpresident scottwalker4president scottwalkerforpresident", "Donald Trump" : "donaldtrump realdonaldtrump teamdonaldtrump teamtrump trump2016 donaldtrump2016 donaltrump4president donaldtrumpforpresident trump4president trumpforpresident"}

stopwords = ["@", "a", "about", "above", "across", "after", "again", "against", "all", "almost", "alone", "along", "already", "also", "although", "always", "among", "an", "and", "another", "any", "anybody", "anyone", "anything", "anywhere", "are", "area", "areas", "around", "as", "ask", "asked", "asking", "asks", "at", "away", "b", "back", "backed", "backing", "backs", "be", "became", "because", "become", "becomes", "been", "before", "began", "behind", "being", "beings", "best", "better", "between", "big", "both", "but", "by", "c", "came", "can", "cannot", "case", "cases", "certain", "certainly", "clear", "clearly", "come", "could", "d", "did", "differ", "different", "differently", "do", "does", "done", "down", "down", "downed", "downing", "downs", "during", "e", "each", "early", "either", "end", "ended", "ending", "ends", "enough", "even", "evenly", "ever", "every", "everybody", "everyone", "everything", "everywhere", "f", "face", "faces", "fact", "facts", "far", "felt", "few", "find", "finds", "first", "for", "four", "from", "full", "fully", "further", "furthered", "furthering", "furthers", "g", "gave", "general", "generally", "get", "gets", "give", "given", "gives", "go", "going", "good", "goods", "got", "great", "greater", "greatest", "group", "grouped", "grouping", "groups", "h", "had", "has", "have", "having", "he", "her", "here", "herself", "high", "high", "high", "higher", "highest", "him", "himself", "his", "how", "however", "i", "if", "important", "in", "interest", "interested", "interesting", "interests", "into", "is", "it", "its", "itself", "j", "just", "k", "keep", "keeps", "kind", "knew", "know", "known", "knows", "l", "large", "largely", "last", "later", "latest", "least", "less", "let", "lets", "like", "likely", "long", "longer", "longest", "m", "made", "make", "making", "man", "many", "may", "me", "member", "members", "men", "might", "more", "most", "mostly", "mr", "mrs", "much", "must", "my", "myself", "n", "necessary", "need", "needed", "needing", "needs", "never", "new", "new", "newer", "newest", "next", "no", "nobody", "non", "noone", "not", "nothing", "now", "nowhere", "number", "numbers", "o", "of", "off", "often", "old", "older", "oldest", "on", "once", "one", "only", "open", "opened", "opening", "opens", "or", "order", "ordered", "ordering", "orders", "other", "others", "our", "out", "over", "p", "part", "parted", "parting", "parts", "per", "perhaps", "place", "places", "point", "pointed", "pointing", "points", "possible", "present", "presented", "presenting", "presents", "problem", "problems", "put", "puts", "q", "quite", "r", "rather", "really", "right", "right", "room", "rooms", "s", "said", "same", "saw", "say", "says", "second", "seconds", "see", "seem", "seemed", "seeming", "seems", "sees", "several", "shall", "she", "should", "show", "showed", "showing", "shows", "side", "sides", "since", "small", "smaller", "smallest", "so", "some", "somebody", "someone", "something", "somewhere", "state", "states", "still", "still", "such", "sure", "t", "take", "taken", "than", "that", "the", "their", "them", "then", "there", "therefore", "these", "they", "thing", "things", "think", "thinks", "this", "those", "though", "thought", "thoughts", "three", "through", "thus", "to", "today", "together", "too", "took", "toward", "turn", "turned", "turning", "turns", "two", "u", "under", "until", "up", "upon", "us", "use", "used", "uses", "v", "very", "w", "want", "wanted", "wanting", "wants", "was", "way", "ways", "we", "well", "wells", "went", "were", "what", "when", "where", "whether", "which", "while", "who", "whole", "whose", "why", "will", "with", "within", "without", "work", "worked", "working", "works", "would", "x", "y", "year", "years", "yet", "you", "young", "younger", "youngest", "your", "yours", "z"]

candidate_stop_words = {'Ben Carson': ['realbencarson','bencarson','drbencarson','teamcarson','teambencarson','bencarson2016','carson2016','carson4president','carsonforpresident','bencarson4president','bencarsonforpresident'],'Bernie Sanders': ['berniesanders','sensanders','teambernie','teamberniesanders','bernie2016','sanders2016','berniesanders2016','sanders4president','sandersforpresident','bernie4president','bernieforpresident','berniesanderse4president','berniesanderseforpresident'],'Carly Fiorina': ['carlyfiorina','fiorina','teamcarly','teamfiorina','teamcarlyfiorina','carly2016','carly4president','carlyforpresident','carlyfiorina4president','carlyfiorinaforpresident','fiorina4president','fiorinaforpresident'],'Donald Trump': ['donaldtrump','realdonaldtrump','teamdonaldtrump','teamtrump','trump2016','donaldtrump2016','donaltrump4president','donaldtrumpforpresident','trump4president','trumpforpresident'],'George Pataki': ['governorpataki','govpataki','pataki','georgepataki','pataki4president','patakiforpresident','georgepataki4president','georgepatakiforpresident','teampataki'],'Hillary Clinton': ['hillaryclinton','hillary','teamhillary','teamclinton','teamhillaryclinton','hillary2016','clinton2016','hillaryclinton2016','hillaryforamerica','hillary4america','hillaryforpresident','hillary4president'],'Jeb Bush': ['jebbush','teamjeb','teamjebbush','jeb2016','bush2016','jebbush2016','jeb','jeb4president','jebforpresident','jebbush4president','jebbushforpresident'],'Lincoln Chafee': ['lincolnchafee','chafee','teamchafee','teamlincolnchafee','chafee2016','lincolnchafee2016','chafeeforpresident','chafee4president'],'Lindsey Graham': ['linseygrahamsc','lindseygraham','grahamblog','senlindseygraham','teamgraham','teamlindseygraham','graham2016','lindseygraham2016','graham4president','grahamforpresident','lindseygraham4president','lindseygrahamforpresident'],'Marco Rubio': ['marcorubio','rubio2016','marcorubio2016','teammarco','teammarcorubio','marco4president','marcoforpresident','rubio4president','rubioforpresident','marcorubio4president','marcorubioforpresident'],"Martin O'Malley": ['governoromalley','martinomalley','teamomalley','teammartinomalley','omalley2016','martinomalley2016','omalley4president','omalleyforpresident'],'Mike Huckabee': ['govmikehuckabee','mikehuckabee','teamhuckabee','teammikehuckabee','huckabee2016','mikehuckabee2016','huckaboom','huckabee4president','huckabeeforpresident','mikehuckabee4president','mikehuckabeeforpresident'],'Rand Paul': ['randpaul','drrandpaul','senatorrandpaul','teamrand','teamrandpaul','randpaul2016','rand2016','standwithrand','rand4president','randforpresident','paul4president','paulforpresident','randpaul4president','randpaulforpresident'],'Rick Perry': ['governorperry','rickperry','teamrickperry','perry2016','rickperry2016','perry4president','perryforpresident','rickperry4president','rickperryforpresident'],'Rick Santorum': ['ricksantorum','santorum2016','teamsantorum','teamricksantorum','santorum4president','santorumforpresident','ricksantorum4president','ricksantorumforpresident'],'Scott Walker': ['scottwalker','teamscottwalker','scottwalker2016','walker4president','walkerforpresident','scottwalker4president','scottwalkerforpresident'],'Ted Cruz': ['tedcruz','sentedcruz','teamcruz','teamtedcruz','tedcruz2016','cruzcrew','cruz4president','cruzforpresident','tedcruz4president',
  'tedcruzforpresident']}

def return_last_tweets():
    current_epoch_time = int(time.time())
    last_day = (current_epoch_time-86400)*1000
    all_search = ""
    for key in candidate_search:
        all_search += (candidate_search[key] + " ")
    client = MongoClient()
    db = client.fletcher.tweets
    tweets = []
    query = db.aggregate([
            {"$match":{"$text":{"$search":all_search}}},
            {"$match":{"timestamp_ms":{"$gte":last_day}}}])
    for tweet in query:
        try:
            tweets.append({
                            'text':tweet['text'],
                            'screen_name':tweet['screen_name'],
                            'timestamp':tweet['timestamp_ms'],
                            'profile_img':tweet['profile_img']
                        })
        except:
            pass
    sorted_tweets = sorted(tweets, key=itemgetter('timestamp'))
    return sorted_tweets

def return_map_tweets(day, candidate="", all_results=0):
    start_time = datetime.strptime(day, "%Y-%m-%d").date()
    start_time = int(start_time.strftime('%s'))*1000
    end_time = start_time + 86399999
    if all_results==1:
        start_time = 0
        end_time = (today_epoch+86400)*1000
    client = MongoClient()
    db = client.fletcher.tweets
    tweets = {}
    if candidate != "":
        query = db.aggregate([
            {"$match":{"$text":{"$search":candidate_search[candidate_slugs[candidate]]}}},
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

def return_tweets(day, search_terms="", all_results=0):
    today_epoch = int(date.today().strftime('%s'))
    start_time = (today_epoch - (day*86400))*1000
    end_time = start_time + 86399999
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

def tweet_bootstrapper(dict, n=0):
    bootstrap_dict = {}
    for key in all_fips:
        try:
            volume = dict[key]['volume']
            sentiment = dict[key]['sentiment']
        except:
            volume = 0
            sentiment = 0
        if volume < 100:
            new_sent, new_vol, weight, new_mult = 0, 0, 10, 0
            for county in nearest_counties[key]:
                try:
                    new_vol += dict[county]['volume']*weight
                    new_sent += dict[county]['sentiment']*weight
                    new_mult += weight
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
        return tweet_bootstrapper(bootstrap_dict, n)
    for key in bootstrap_dict:
        bootstrap_sent = bootstrap_dict[key]['sentiment']
        if bootstrap_sent < 0:
            bootstrap_sent = -((-bootstrap_sent)**(0.3))
        else:
            bootstrap_sent **= (0.3)
        bootstrap_dict[key]['sentiment'] = bootstrap_sent
        bootstrap_dict[key]['volume'] *= 1500
    return bootstrap_dict

def convert_tweet_bootstrapper_to_tsv(bootstrap_dict):
    dicts = {}
    sentiment_dict = [{'id' : 'id', 'rate' : 'rate'}]
    volume_dict = [{'id' : 'id', 'rate' : 'rate'}]
    for key in all_fips:
        try:
            sentiment_dict.append({"id":key,"rate":bootstrap_dict[key]['sentiment']})
        except:
            sentiment_dict.append({"id":key,"rate":0})
        try:
            volume_dict.append({"id":key,"rate":bootstrap_dict[key]['volume']})
        except:
            volume_dict.append({"id":key,"rate":0})
    return {"sentiment": sentiment_dict, "volume": volume_dict}

def write_map_tsv(day, candidate, file_name, recursive):
    tweets = return_map_tweets(day, candidate)
    tweets = tweet_bootstrapper(tweets,recursive)
    bootstrapped_tweets = convert_tweet_bootstrapper_to_tsv(tweets)
    with open('static/tsv/' + file_name + '_sentiment.tsv', 'w') as f:
        [f.write('{0}\t{1}\n'.format(key['id'], key['rate'])) for key in bootstrapped_tweets['sentiment']]
    with open('static/tsv/' + file_name + '_volume.tsv', 'w') as f:
        [f.write('{0}\t{1}\n'.format(key['id'], key['rate'])) for key in bootstrapped_tweets['volume']]

def create_map_tsv(day, candidate, recursive):
    file_name = day + "_" + candidate
    if day != 0:
        if os.path.exists("/static/tsv/" + file_name + "sentiment.tsv"):
            pass
        else:
            write_map_tsv(day, candidate, file_name, recursive)
    else:
        write_map_tsv(day, candidate, file_name, recursive)

def get_candidates_js_object(time=0, n=0, group_val="top", individual=""):
    candidates_object = []
    js_date = date.today() - timedelta(time)
    js_date = js_date.strftime('%Y-%m-%d')
    if individual != "":
        iterator = [individual]
    else:
        iterator = candidate_lists[group_val]
    for key in iterator:
        total_volume = 0
        total_sent_vol = 0
        search_terms = candidate_search[key]
        tweets = return_tweets(time, search_terms)
        boosted_tweets = tweet_bootstrapper(tweets,n)
        candidate_dict = { "group" : key, "date" : js_date }
        for county in boosted_tweets:
            county_volume = boosted_tweets[county]['volume']
            total_volume += county_volume
        try:
            candidate_dict['value'] = total_volume
        except:
            candidate_dict['value'] = 0
        candidates_object.append(candidate_dict)
    return candidates_object

def get_all_candidates_js_objects(time=1, group_val="top", individual=""):
    all_candidates_object = []
    for x in reversed(range(time)):
        all_candidates_object += get_candidates_js_object(x, 0, group_val, individual)
    return all_candidates_object

def get_topics(candidate, day):
    start_time = datetime.strptime(day, "%Y-%m-%d").date()
    start_time = int(start_time.strftime('%s'))*1000
    end_time = start_time + 86399999
    try:
        client = MongoClient()
        tweets = client.fletcher.tweets
        tweets = tweets.aggregate([
            {"$match":{"$text":{"$search":candidate_search[candidate_slugs[candidate]]}}},
            {"$match":{"timestamp_ms":{"$gte":start_time,"$lt":end_time}}}])
        documents = []
        pattern = re.compile("[^a-zA-Z ]")
        for tweet in tweets:
            documents.append(pattern.sub('', tweet['text']))
        stoplist = set(candidate_stop_words[candidate_slugs[candidate]] + stopwords)
        texts = [[word for word in document.lower().split() if word not in stoplist]
                for document in documents]
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1
        texts = [[token for token in text if frequency[token] > 1]
                for text in texts]
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=3, update_every=1, chunksize=10000, passes=10)
        return lda.print_topics(3)
    except:
        return None

def get_topic_dictionary(candidate, day):
    start_time = datetime.strptime(day, "%Y-%m-%d").date()
    start_time = int(start_time.strftime('%s'))*1000
    end_time = start_time + 86399999
    client = MongoClient()
    tweets = client.fletcher.tweets
    tweets = tweets.aggregate([{"$match":{"$text":{"$search":candidate_search[candidate_slugs[candidate]]}}},
                               {"$match":{"timestamp_ms":{"$gte":start_time,"$lt":end_time}}}])
    documents = []
    pattern = re.compile("[^a-zA-Z ]")
    for tweet in tweets:
        try:
            documents.append(pattern.sub('', tweet['text']))
        except:
            continue
    stoplist = set(candidate_stop_words[candidate_slugs[candidate]] + stopwords)
    texts = [[word for word in document.lower().split() if word not in stoplist]
            for document in documents]
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [[token for token in text if frequency[token] > 1]
            for text in texts]
    dictionary = corpora.Dictionary(texts)
    topics = []
    for item in dictionary.items():
        topics.append({"text" : item[1], "size" : item[0]})
    return topics




