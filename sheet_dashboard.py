#this code will import the total number of eventbrite tickets sold for an event at the time the code is run and export the count to a trello card and google sheets


from collections import Counter
import requests
import json
from configparser import ConfigParser

config = ConfigParser()
config.read('config.cfg')

eventbrite_token = config['user_info']['eventbrite_token']
event_id = config['eventbrite_ids']['event_id']#update event_id for each event
event_name = 'DataScience'
trello_key = config['user_info']['trello_key']
trello_token = config['user_info']['trello_token']
card_id = config['trello_ids']['card_id']#update card_id for each trello card

spreadsheet_id = config['sheets_ids']['sheets_id'] #update sheets_id for each google sheets

response = requests.get("https://www.eventbriteapi.com/v3/users/me/?token=" + eventbrite_token) #log into eventbrite

attendees = requests.get( "https://www.eventbriteapi.com/v3/events/" +event_id+ "/attendees/?token=" + eventbrite_token) #get event details
#jprint(attendees.json())

pagination = attendees.json()['pagination']
count = pagination['object_count'] #get total number of orders
print(count)
#get current date and time to be included in sheets
from datetime import date
today = date.today().strftime('%Y-%m-%d')

#----sheets
#leave this untouched
#define gsheet_api_check to obtain permission; taken from tutorial (https://towardsdatascience.com/how-to-import-google-sheets-data-into-a-pandas-dataframe-using-googles-api-v4-2020-f50e84ea4530)
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
def gsheet_api_check(SCOPES):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

#leave this untouched
#define pull_sheet_date to import spreadsheet from google sheets
from googleapiclient.discovery import build
def pull_sheet_data(SCOPES,SPREADSHEET_ID,DATA_TO_PULL):
    creds = gsheet_api_check(SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=DATA_TO_PULL).execute()
    values = result.get('values', [])
    
    if not values:
        print('No data found.')
    else:
        rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                  range=DATA_TO_PULL).execute()
        data = rows.get('values')
        print("COMPLETE: Data copied")
        return data

#import the desired spreadsheet from google sheets
#input the spreadsheet id for the desired spreadsheet

import pandas as pd
SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] #leave this untouched
SPREADSHEET_ID = spreadsheet_id #get id from hyperlink and insert here; between "https://docs.google.com/spreadsheets/d/" and "/edit"
DATA_TO_APPEND = 'Sheet2!A1' #set where you want the data to appear

#add dataframe into a tab in desired google sheets
from googleapiclient import discovery
def append_sheet_data(SCOPES,SPREADSHEET_ID,DATA_TO_APPEND):
    '''this function is for appending data into google sheets'''
    creds = gsheet_api_check(SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().append(
        valueInputOption = 'RAW',
        spreadsheetId=SPREADSHEET_ID,
        body = {"majorDimension" : 'ROWS', 
                "values" : [[event_name, today, count]] },
        range=DATA_TO_APPEND).execute()

append_sheet_data(SCOPES,SPREADSHEET_ID,DATA_TO_APPEND)

  # This code will post comment to trello card


url = "https://api.trello.com/1/cards/"+card_id+"/actions/comments" #url for the trello card
query = {
   'key': trello_key,
   'token': trello_token,
   'text': 'eventbrite: ' + str(count) #add the text to the comment here
}

response = requests.request(
   "POST",
   url,
   params=query
)

print(response.text)
