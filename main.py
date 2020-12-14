import twitter
import tweepy
import simplekml
from cluster import KMeansClustering
from cluster.util import centroid
from geopy import geocoders

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''

GOOGLE_MAPS_SECRET_KEY = ''

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
api = twitter.Twitter(auth=auth)

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth)

geocoder = geocoders.GoogleV3(api_key=GOOGLE_MAPS_SECRET_KEY)

WORLD_WOE_ID = 1

world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)
mainTrend = world_trends[0]['trends'][:1]

TWEET_SAMPLE_SIZE = 1000
CLUSTER_COUNT = 3
i = 0
for trend in mainTrend:
    location_list = list()
    for tweet in tweepy.Cursor(api.search, q=trend['query']).items(TWEET_SAMPLE_SIZE):
        if tweet.user.location:
            print(i)
            i += 1
            try:
                location = geocoder.geocode(tweet.user.location)
                location_list.append({"lat": location.latitude, "lon": location.longitude})
            except Exception as e:
                print("An exception occurred: ")
                print(e)
                pass

with open('out.txt', 'w') as f:
    print(location_list, file=f)

cluster = KMeansClustering([(l['lat'], l['lon']) for l in location_list])
centroids = [centroid(c) for c in cluster.getclusters(CLUSTER_COUNT)]

kml_clusters = simplekml.Kml()
for i, c in enumerate(centroids):
    kml_clusters.newpoint(name='Cluster {}'.format(i), coords=[(c[1], c[0])])
    kml_clusters.save('{}.kml'.format(trend['query']))
