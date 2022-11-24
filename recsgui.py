import PySimpleGUI as sg
import NERecs as recs
import pandas as pd
searchDetailsCol= [ 
            [sg.Text('Welcome to NERecs')],
            [sg.Text('Enter current location (lat,long)'), sg.Input(key='location')],
            [sg.Text('Max distance away (m)'), sg.Input(key='distance')],
            [sg.Text('Search for:'), sg.Input(key='query')],
            [sg.Button('Begin Search'), sg.Cancel()]
            ]

userHistCol= [
            [sg.Text('Please list previous places you have enjoyed'), sg.Input(key='-INPUT-0-')],
            [sg.Button('+ Places')]
            ]
layout = [
    [sg.Column(searchDetailsCol),
    sg.VSeperator(),
    sg.Column(userHistCol, key='-COL-')]
]
window = sg.Window('Get Recs', layout)
inputCount=0
def retrieveUserInput(num_input):
    queryInfo={}
    restHistory=[]
    queryInfo.update({'curr_location': values['location']})
    queryInfo.update({'distance': values['distance']})
    queryInfo.update({'search_term': values['query']})
    
    while num_input>=0:
        restHistory.append(values['-INPUT-' + str(num_input) +'-'])
        num_input-=1

    return queryInfo, restHistory

while True:             
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    if event =='+ Places':
        inputCount += 1
        window.extend_layout(window['-COL-'],[[sg.Text('Location '+str(inputCount+1)), sg.Input(key=f'-INPUT-{inputCount}-')]])
        
    if event =='Begin Search':
        searchInfo, restInput= retrieveUserInput(inputCount)
        masterRestaurantDict={}
        temp_search_ids=recs.get_place_ids(searchInfo['search_term'], searchInfo['distance'], searchInfo['curr_location'])
        user_ids=recs.get_user_ids(restInput)
        search_ids=[id for id in temp_search_ids if id not in user_ids]
        masterRestDf = recs.get_restaurant_data(search_ids)
        masterUserDf= recs.get_restaurant_data(user_ids)
        
        recs.scrub_review(masterRestDf)
        recs.scrub_review(masterUserDf)
        recs.remove_stop_words(masterRestDf)
        recs.remove_stop_words(masterUserDf)

        result=recs.tf_idf_vectorize(masterRestDf, masterUserDf)
        sim=recs.similarity_calc(result)
        values=recs.extract_similarity(sim, len(user_ids))
        final_recs=recs.get_sim_restaurants(masterRestDf, masterUserDf, values)
        export_df=masterRestDf[masterRestDf['name'] in final_recs.keys()]
        
        print(final_recs)
        
        break
window.close()

