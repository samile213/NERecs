
from doctest import master
import pandas as pd
import numpy as np
import googlemaps

import requests

input = 'restaurants'
inputtype= 'textquery'
api_key = 'AIzaSyAXVtpkugUiX-ToYYiBDJ57USR52jrfcls'
radius=2000
# location = (latitude,longitude) below for 426 University Ave
location = (43.6505388,-79.386292)
fields = 'name', 'formatted_address', 'url', 'rating', 'user_ratings_total', 'price_level'
# To reduce number of calls to Places API
mapclient = googlemaps.Client(api_key)

# response = mapclient.places(query=input, location=location, radius=radius)
# results=response.get('results')
# restaurantID=[]
# for restaurantsDict in results:
#     restaurantID.append(restaurantsDict.get('place_id'))
# # results = response.get('name')
# print(restaurantID)

IDs=['ChIJs_Gr4rE0K4gR4PCci36eEkg', 'ChIJz9AjljTL1IkRjqIDanJTWKE', 'ChIJe8kdIzPL1IkR95b8l3Aazt8', 'ChIJibO6GcY0K4gRR0nml4yEusI', 
'ChIJySHpzNA0K4gRugQVPpaq0YU', 'ChIJqWFmAzLL1IkRSTELEp2iOHI', 'ChIJX6jLpdU1K4gRE-_wl8DkVhg', 
'ChIJ_SEys7U0K4gRvk-B5aDrpmE', 'ChIJLbNPx9E0K4gRBywc1ZieRe8', 'ChIJ34QZxso0K4gRjxnB_LkcDMI', 'ChIJKSp50NI0K4gR6C6L3yYqpYY', 'ChIJr_tCsVg1K4gREHA5C-YHJys', 'ChIJX7Gdv8s0K4gRywZ3zD4I9w8', 'ChIJHc8cgJU0K4gRKd0dd0dVvws', 'ChIJVVXhcts0K4gR9wRXqbtY0rY', 'ChIJT6VInRo1K4gRS9yQ4qAb8Cg', 
'ChIJna5xqdE0K4gRY2U5hw6ZXYI', 'ChIJdSB4Yvo1K4gRhtIxDjQDCMM', 'ChIJK2lqhdM0K4gRRLfXBys5VBc', 'ChIJ94c0RLI0K4gRI1_A4rVy_Qs']
# Master dictionary for all search results
masterRestaurantDict={}

for i in range(2):
    responseDetails={}
    details=mapclient.place(place_id=IDs[i],fields=fields)
    
    key_details=details.get('result')

    # Create nested dictionary for restaurant specific details
    responseDetails.update({'name': key_details['name']})
    responseDetails.update({'rating': key_details['rating']})
    responseDetails.update({'address': key_details['formatted_address']})
    responseDetails.update({'website': key_details['url']})
    responseDetails.update({'price': key_details['price_level']})
    responseDetails.update({'number of ratings': key_details['user_ratings_total']})
    masterRestaurantDict.update({'result'+str(i+1): responseDetails})
tempDf=pd.DataFrame(masterRestaurantDict)
masterRestDf=tempDf.transpose()
print(masterRestDf)