# import nltk
# from nltk.util import bigrams
# n = 1
# sentence = ['you','eat', 'flour', 'juice', 'terrible', 'friendly']
# sent_bigrams = bigrams(sentence)
# print(list(bigrams(sentence)))
import googlemaps
import constants as const
import pandas as pd

fields='name','place_id', 'formatted_address'
def find_user_places(location_name):
    masterUserRestaurantDict={}
    mapclient = googlemaps.Client(const.API_KEY)
    ids=[]
    for i in range(len(location_name)):
        # print(location_name[i])
        potential_ids=mapclient.find_place(input=location_name[i], input_type='textquery', fields=const.USER_FIELDS)
        temp_id=potential_ids.get('candidates')[0]
        # print(temp_id)
        ids.append(temp_id['place_id'])
    return ids

def get_place_ids(search_query, dist, coords):
    search_ids=[]
    mapclient = googlemaps.Client(const.API_KEY)
    potential_ids=mapclient.places(query=search_query, radius=dist, location=coords)
    # print(potential_ids)
    temp_id=potential_ids.get('results')
    for place in range(len(temp_id)):
        search_ids.append(temp_id[place]['place_id'])
    return search_ids


# user_info=find_user_places(['taste bender', 'zenq', 'chipotle'])
search=get_place_ids('bubble tea', 2000, (43.6505388,-79.386292))
print(search)


