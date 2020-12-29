'''
// Important notes about Streamlit \\
The framework doesn't handle event binding (i.e. a specific function to be
called when a user clicks on a button)! When a button is pressed, the whole
script is rerun.
'''

import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import streamlit as st

import dataclasses
from gamestate import persistent_game_state

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# here enter the id of your google sheet
SAMPLE_SPREADSHEET_ID_input = '1lMkLiPKYXT1qCDeLK1qRDF3yPMkCWJtHrJ1LTsHhlgA'
SAMPLE_RANGE_NAME = 'A1:AA1000'
COLUMN_VOC = 'Voc'
COLUMN_TRANSLATION_VOC = 'Traduction voc'

# decorator automatically does the __init__() and __repr__()
@dataclasses.dataclass
class GameState:
    word: str = ''
    translation: str = ''
    game_number : int = 0
    game_over: bool = False

def loadSpreadsheet():
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])

    if not values_input:
        print('No data found.')

def randomWord(df, column_name):
    translation = None
    while(not translation or translation==''):
        random_word = df[column_name].sample(n=1).values[0]
        translation = df[df[column_name]==random_word]['Traduction ' + column_name.lower()].values[0]
    return random_word, translation

loadSpreadsheet()

df_data = pd.DataFrame(values_input[1:], columns=values_input[0])

state = persistent_game_state(initial_state=GameState())

if st.button('Générer un mot'):
    state.word, state.translation = randomWord(df_data, COLUMN_VOC)
    state.game_number += 1
    state.game_over = False

if not state.game_over:
    guess = None
    st.write(state.word)
    guess = st.text_input("Votre traduction :", key=state.game_number)
    if guess:
        if guess != state.translation:
            st.write("Mauvaise réponse !")
        else:
            st.write("Bonne réponse !")
            state.game_over = True