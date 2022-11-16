
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
from cleantext import clean


def get_user_ids(location_name):
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
    temp_id=potential_ids.get('results')
    for place in range(len(temp_id)):
        search_ids.append(temp_id[place]['place_id'])
    return search_ids

def get_restaurant_data(list_ids):
    mapclient = googlemaps.Client(const.API_KEY)
    restaurantDf=pd.DataFrame(columns=['name', 'rating', 'price', 'address', 'reviews'])
    # tempDf=pd.DataFrame(columns=['name', 'rating', 'price_level', 'formatted_address', 'reviews'])


    for i in range(len(list_ids)):

        text_reviews=[]
        responseDetails={}

        details=mapclient.place(place_id=list_ids[i],fields=const.FIELDS)        
        key_details=details.get('result')

        # Check to make sure no keys missing from Google Place API call, otherwise fill in None value
        price_level = key_details['price_level'] if 'price_level' in key_details else None
        name = key_details['name'] if 'name' in key_details else None
        rating = key_details['rating'] if 'rating' in key_details else None
        address = key_details['formatted_address'] if 'formatted_address' in key_details else None
        reviews= key_details['reviews'] if 'reviews' in key_details else None

        # Create nested dictionary for restaurant specific details

        responseDetails.update({'name': name})
        responseDetails.update({'rating': rating})
        responseDetails.update({'address': address})
        responseDetails.update({'price': price_level})
        
        # responseDetails.update({'number of ratings': key_details['user_ratings_total']})
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
# def bigram_generator():
#     for m in range(len(masterRestDf['reviews'])):
#         word_list=masterRestDf['reviews'][m]
#         masterRestDf['reviews'][m]=list(bigrams(word_list))
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
    # print(bigram_list)
    for r in range(len(restaurantDf['reviews'])):
        if restaurantDf['reviews'][r] is None:
            bigram_list.append(['no reviews'])
            continue
        bigram_list.append(restaurantDf['reviews'][r])
    # print(bigram_list)
    tf_idf_mat=tfidf.fit_transform(bigram_list)
    # If want to print out bigram tokens and the tfidf values  for each place
    # Doc_Term_Matrix = pd.DataFrame(tf_idf_mat.toarray(),columns= tfidf.get_feature_names_out())
    # print(Doc_Term_Matrix)
    return tf_idf_mat

def similarity_calc(matrix):
    corr_matrix=linear_kernel(matrix,matrix)
    return corr_matrix


    # masterRestDf['bigram_vector']=np.nan
    # for gram_list in range(len(masterRestDf['reviews'])):
    #     temp_list=masterRestDf['reviews'][gram_list]
    #     for gram in gram_list:
    #         if gram not in masterRestDf['bigram_vector']:

# if __name__ == '__main__':
#     # Master dictionary for all search results
#     masterRestaurantDict={}
#     search_ids=get_place_ids(search_term, coords, radius)
#     user_ids=get_user_ids(input_from_GUI)
    # masterRestDf = get_restaurant_data(['ChIJYdY38U01K4gRtrhyoMT3Ewg', 'ChIJhcb-7yg1K4gRm1AMPBW4SL0', 'ChIJmdnMwMs0K4gRDnymN6VwdoY', 'ChIJGckzrrU1K4gRl0Q1zR5b1dM', 'ChIJ9-UFZME0K4gR3oxH_FuLGzU', 'ChIJP0dCb1U1K4gRJRQ5BgAUXgQ', 'ChIJ8bG6Onk1K4gRkh1W8ms4szM', 'ChIJOf3wKVM1K4gRfQQRV1_Es50', 'ChIJsw0Fq441K4gRn_IOhCy2OVs', 'ChIJAdcAqpo1K4gR8BGhc3fBQ3w', 'ChIJkRdxZcQ0K4gRmiHOiDOsmn8', 'ChIJ3VCZDQI1K4gRLIKbF0xKF0w', 'ChIJqT2IEFQ1K4gRqd45SgiiJfc', 'ChIJBbS8kNbL1IkRYz8cS_ri2nQ', 'ChIJ8xilNobL1IkRutvbxnxTdRM', 'ChIJM97DlSA1K4gRP0d-qEXSYV0', 'ChIJSc-6ouQ1K4gRNFLsmzcb6aI', 'ChIJD083J3U1K4gR7pzWv78x8Sc', 'ChIJveqjvBA1K4gRbzas_ZmAs3U', 'ChIJd8ZUPjs1K4gRUGi_EMCSCVI'])
    # print(masterRestDf)   
#  masterUserDf= get_restaurant_data(user_ids)
#     scrub_review()
#     remove_stop_words()
#     # bigram_generator()
#     # print(masterRestDf['reviews'][0])
#     result=tf_idf_vectorize([masterRestDf['reviews'][0]])
#     sim=similarity_calc(result)
#     print(sim)
#     # print(tfidf.get_feature_names_out())
    # get_restaurant_data(['ChIJYdY38U01K4gRtrhyoMT3Ewg'])
    # (['ChIJveqjvBA1K4gRbzas_ZmAs3U'])
    # (['ChIJYdY38U01K4gRtrhyoMT3Ewg'])


# with pd.option_context('display.max_colwidth',100):
#     print(masterRestDf)

