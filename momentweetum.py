import flask
from pymongo import MongoClient
import time

#---------- BUILT MOMENTUM MODEL ----------------#
areas = ["bronx","harlem","upper_west","upper_east","midtown","downtown","brooklyn","queens","san_fran","west_bay","east_bay","south_bay"]

def find_momentum():
    current_time = int(time.time())
    five_min = (current_time - 300) * 1000
    ten_min = (current_time-600) * 1000
    fifteen_min = (current_time-900) * 1000
    client = MongoClient()
    db = client.fletcher.tweets
    five_counts = {}
    ten_counts = {}
    fifteen_counts = {}
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
    When A POST request with json data is made to this uri,
    return the momentum for the last 5 minutes
    """
    # Get decision score for our example that came with the request
    # data = flask.request.json

    x = np.matrix(data["example"])
    score = PREDICTOR.predict_proba(x)
    # Put the result in a nice dict so we can send it as json
    results = {"score": score[0,1]}
    return flask.jsonify(results)

#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
app.run(host='0.0.0.0', port=5000)
