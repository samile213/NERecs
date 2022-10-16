import PySimpleGUI as sg

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
    print(num_input)
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
        print(restInput)
        break
window.close()

