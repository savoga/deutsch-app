import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# here enter the id of your google sheet
SAMPLE_SPREADSHEET_ID_input = '1lMkLiPKYXT1qCDeLK1qRDF3yPMkCWJtHrJ1LTsHhlgA'
SAMPLE_RANGE_NAME = 'A1:AA1000'
COLUMN_VOC = 'Voc'
COLUMN_TRANSLATION_VOC = 'Traduction voc'

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

def randomWord(column_name):
    translation = None
    while(not translation or translation==''):
        random_word = df_data[column_name].sample(n=1).values[0]
        translation = df_data[df_data[column_name]==random_word]['Traduction ' + column_name.lower()].values[0]
    return random_word, translation

def isCorrect(user_answer, correct_answer):
    if user_answer==correct_answer:
        st.write('Correct!')
    else:
        st.write('Wrong!')

loadSpreadsheet()
df_data = pd.DataFrame(values_input[1:], columns=values_input[0])
user_input = None

if st.button(COLUMN_VOC):
    random_word, translation = randomWord(COLUMN_VOC)
    st.write(random_word)
    user_input = st.text_input("Your answer")
if user_input:
    isCorrect(user_input, translation)