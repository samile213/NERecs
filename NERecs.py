
from doctest import master
import pandas as pd
import numpy as np
import googlemaps
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
import nltk
# from nltk.util import bigrams
from nltk.corpus import stopwords
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import string
import constants as const


def get_user_ids(location_name):
    mapclient = googlemaps.Client(const.API_KEY)
    ids=[]
    for i in range(len(location_name)):
        # print(location_name[i])
        potential_ids=mapclient.find_place(input=location_name[i], input_type='textquery', fields=const.USER_FIELDS)
        temp_id=potential_ids.get('candidates')
        # print(temp_id)
        ids.append(temp_id['place_id'])
    return ids

def get_place_ids(search_query, dist, coords):
    search_ids=[]
    mapclient = googlemaps.Client(const.API_KEY)
    potential_ids=mapclient.places(query=search_query, radius=dist, location=coords)
    temp_id=potential_ids.get('results')
    for place in range(len(temp_id)):
        search_ids.append(temp_id[place]['place_id'])
    return search_ids

def get_restaurant_data():
    mapclient = googlemaps.Client(const.API_KEY)

    for i in range(2):
        text_reviews=[]
        responseDetails={}
        details=mapclient.place(place_id=const.IDS[i],fields=const.FIELDS)
        
        key_details=details.get('result')

        # Create nested dictionary for restaurant specific details
        responseDetails.update({'name': key_details['name']})
        responseDetails.update({'rating': key_details['rating']})
        responseDetails.update({'address': key_details['formatted_address']})
        responseDetails.update({'website': key_details['url']})
        responseDetails.update({'price': key_details['price_level']})
        responseDetails.update({'number of ratings': key_details['user_ratings_total']})
        for r in key_details['reviews']:
            text_reviews.append(r['text'])
        responseDetails.update({'reviews': text_reviews})
        masterRestaurantDict.update({'result'+str(i+1): responseDetails})
    tempDf=pd.DataFrame(masterRestaurantDict)
    return tempDf.transpose()



# Want to correct spelling, convert contractions, remove punctuation/emoji, lower case everything, remove stopwords, 
# to lowercase, text is the dataframe value text
def scrub_review():
    for j in range(len(masterRestDf['reviews'])):
        tempArr=[]
        for s in masterRestDf['reviews'][j]:
            tempStr=s.translate(str.maketrans('', '', string.punctuation))
            tempStr=tempStr.translate(str.maketrans('','', string.digits))
            tempStr=" ".join(tempStr.split())
            tempStr=tempStr.lower()
            tempStr=word_tokenize(tempStr)
            if tempStr!='':
                tempArr.append(tempStr)
        masterRestDf['reviews'][j]=tempArr


# remove unnecessary words (i, we, is, was etc.) as well as lemmatize tokens to get root meaning and avoid variation in repetition
def remove_stop_words():
    delete_stopwords=['wouldnt', 'wont', 'werent', 'wasnt', 'isnt', 'not', 'dont', 'didnt', 'werent']
    add_stopwords=['id','youd','wed','']
    new_stopwords = set(stopwords.words('english')).difference(delete_stopwords)

    lemmatizer=WordNetLemmatizer()
    for k in range(len(masterRestDf['reviews'])):
        tokens=[]
        for rev in masterRestDf['reviews'][k]:
            for word in rev:
                if word not in new_stopwords:
                    lem_word=lemmatizer.lemmatize(word)
                    tokens.append(lem_word)
            masterRestDf['reviews'][k]=tokens
# def bigram_generator():
#     for m in range(len(masterRestDf['reviews'])):
#         word_list=masterRestDf['reviews'][m]
#         masterRestDf['reviews'][m]=list(bigrams(word_list))
# Dummy tokenizer function to overwrite preprocessing steps in TfidfVectorizer
def identity_tokenizer(text):
    return text
def tf_idf_vectorize(rest1):
    bigram_list=rest1
    tf_idf_mat=tfidf.fit_transform(bigram_list)
    
    return tf_idf_mat
def similarity_calc(matrix):
    corr_matrix=linear_kernel(matrix,matrix)
    return corr_matrix

tfidf=TfidfVectorizer(tokenizer=identity_tokenizer, lowercase=False, ngram_range=(2,2))
    # masterRestDf['bigram_vector']=np.nan
    # for gram_list in range(len(masterRestDf['reviews'])):
    #     temp_list=masterRestDf['reviews'][gram_list]
    #     for gram in gram_list:
    #         if gram not in masterRestDf['bigram_vector']:

if __name__ == '__main__':
    # Master dictionary for all search results
    masterRestaurantDict={}
    search_ids=get_place_ids(search_term, coords, radius)
    user_ids=get_user_ids(input_from_GUI)
    masterRestDf = get_restaurant_data()
    masterUserDf= get_restaurant_data()
    scrub_review()
    remove_stop_words()
    # bigram_generator()
    # print(masterRestDf['reviews'][0])
    result=tf_idf_vectorize([masterRestDf['reviews'][0]])
    sim=similarity_calc(result)
    print(sim)
    # print(tfidf.get_feature_names_out())


# with pd.option_context('display.max_colwidth',100):
#     print(masterRestDf)

