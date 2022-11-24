
from doctest import master
import pandas as pd
import numpy as np
import googlemaps
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import string
import constants as const
import secret
from cleantext import clean


def get_user_ids(location_name):
    mapclient = googlemaps.Client(secret.API_KEY)
    ids=[]
    for i in range(len(location_name)):
        potential_ids=mapclient.find_place(input=location_name[i], input_type='textquery', fields=const.USER_FIELDS)
        temp_id=potential_ids.get('candidates')[0]
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

def get_restaurant_data(list_ids):
    mapclient = googlemaps.Client(const.API_KEY)
    restaurantDf=pd.DataFrame(columns=['name', 'rating', 'price', 'address', 'reviews'])

    for i in range(len(list_ids)):

        text_reviews=[]
        responseDetails={}

        details=mapclient.place(place_id=list_ids[i],fields=const.FIELDS)        
        key_details=details.get('result')

        # Check to make sure no keys missing from Google Place API call, otherwise fill in None value
        price_level = key_details['price_level'] if 'price_level' in key_details else None
        name = key_details['name'] if 'name' in key_details else None
        rating = key_details['rating'] if 'rating' in key_details else 0
        address = key_details['formatted_address'] if 'formatted_address' in key_details else None
        reviews= key_details['reviews'] if 'reviews' in key_details else None

        # Create nested dictionary for restaurant specific details

        responseDetails.update({'name': name})
        responseDetails.update({'rating': rating})
        responseDetails.update({'address': address})
        responseDetails.update({'price': price_level})
      
        if reviews!=None:
            for r in key_details['reviews']:
                text_reviews.append(r['text'])
            responseDetails.update({'reviews': text_reviews})
        else:
            responseDetails.update({'reviews': None})

        new_row = pd.Series(responseDetails)
        restaurantDf=pd.concat([restaurantDf, new_row.to_frame().T], ignore_index=True)
    return restaurantDf


# Want to correct spelling, convert contractions, remove punctuation/emoji, lower case everything, remove stopwords, 
# to lowercase, text is the dataframe value text
def scrub_review(rest_df):
    if rest_df['reviews'].empty!=None:
        for j in range(len(rest_df['reviews'])):
            if rest_df['reviews'][j] is None:
                continue
            tempArr=[]
            for s in rest_df['reviews'][j]:
                tempStr=s.translate(str.maketrans('', '', string.punctuation))
                tempStr=tempStr.translate(str.maketrans('','', string.digits))
                tempStr=" ".join(tempStr.split())
                tempStr=tempStr.lower()
                tempStr=clean(tempStr, no_emoji=True)
                tempStr=word_tokenize(tempStr)
                if tempStr!='':
                    tempArr.append(tempStr)
            rest_df['reviews'][j]=tempArr

        return rest_df


# remove unnecessary words (i, we, is, was etc.) as well as lemmatize tokens to get root meaning and avoid variation in repetition
def remove_stop_words(rest_df):
    delete_stopwords=['wouldnt', 'wont', 'werent', 'wasnt', 'isnt', 'not', 'dont', 'didnt', 'werent']
    new_stopwords = set(stopwords.words('english')).difference(delete_stopwords)
    if rest_df['reviews'].empty!=None:

        lemmatizer=WordNetLemmatizer()
        for k in range(len(rest_df['reviews'])):
            if rest_df['reviews'][k]!=None:
                tokens=[]
                for rev in rest_df['reviews'][k]:
                    for word in rev:
                        if word not in new_stopwords:
                            lem_word=lemmatizer.lemmatize(word)
                            tokens.append(lem_word)
                    rest_df['reviews'][k]=tokens
        return rest_df

# Dummy tokenizer function to overwrite preprocessing steps in TfidfVectorizer
def dummy(text):
    return text


tfidf=TfidfVectorizer(tokenizer=dummy, analyzer='word',preprocessor=dummy,token_pattern=None, lowercase=False, ngram_range=(2,2), strip_accents='ascii')
def tf_idf_vectorize(restaurantDf, userDf):
    bigram_list=[]
    for k in range(len(userDf['reviews'])):
        if userDf['reviews'][k] is None:
            bigram_list.append(['no reviews'])
            continue
        bigram_list.append(userDf['reviews'][k])
    
    for r in range(len(restaurantDf['reviews'])):
        if restaurantDf['reviews'][r] is None:
            bigram_list.append(['no reviews'])
            continue
        bigram_list.append(restaurantDf['reviews'][r])
    
    tf_idf_mat=tfidf.fit_transform(bigram_list)
    return tf_idf_mat

def similarity_calc(matrix):
    corr_matrix=linear_kernel(matrix,matrix)
    return corr_matrix

def extract_similarity(sim_mat, user_id_qty):
    col=len(sim_mat[0])
    num_search=int(col-user_id_qty)
    cosine_val=np.zeros((user_id_qty,num_search))
   
    for i in range(user_id_qty):
        k=0
        for j in range(user_id_qty, col):
            # Restaurant idx: cos_sim value
            cosine_val[i][k]=sim_mat[i][j]
            k+=1
      
   
    return cosine_val

def get_sim_restaurants(restaurantDf, userDf, cos_sim_mat):
    # Note sorts from smallest to largest, need to iterate backwards later to find highest sim value
    sorted_idx=[]
    final_rest_rec={}
    # Number of places inputted by user (rows in dataframe)
    num_input=userDf.shape[0]
    
    # Try iterating by columns instead of rows since everything should be bundled based on all user input and not one at a time
    for m in range(len(cos_sim_mat)):
        # Flip argsort to be in descending value for cos_sim values instead of increasing
        sorted_idx=np.fliplr(np.argsort(cos_sim_mat, axis=1))
        
    
    for k in range(num_input):
        user_rating=userDf['rating'][k]
        rank=1
        for p in range(len(cos_sim_mat)):
            for i in range(len(cos_sim_mat[0])):
               
                idx=sorted_idx[p,i]
                curr_rating=restaurantDf['rating'].iloc[idx]
                curr_rest=restaurantDf['name'].iloc[idx]
            
                if curr_rating>= (user_rating-0.3) and curr_rest not in final_rest_rec:
                    # p is the ranking from most similar to least
                    final_rest_rec[curr_rest]=rank
                    rank+=1
                    
                else:
                    continue
    return final_rest_rec




