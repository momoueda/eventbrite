from collections import Counter
import requests
import json
from configparser import ConfigParser

config = ConfigParser()
config.read('config.cfg')

eventbrite_token = config['user_info']['eventbrite_token']

event_id = config['eventbrite_ids']['event_id']#update event_id for each event
event_name = 'R&D'
spreadsheet_id = config['sheets_ids']['sheets_id'] #update sheets_id for each google sheets

response = requests.get("https://www.eventbriteapi.com/v3/users/me/?token=" + eventbrite_token) #log into eventbrite

attendees = requests.get( "https://www.eventbriteapi.com/v3/events/" +event_id+ "/attendees/?token=" + eventbrite_token) #get event details
#jprint(attendees.json())

pagination = attendees.json()['pagination']
count = pagination['object_count'] #get total number of orders
print(count)

#----sheets
#leave this untouched
#define gsheet_api_check to obtain permission
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
from pprint import pprint
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
                "values" : [[event_name, 'date', count]] },
        range=DATA_TO_APPEND).execute()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '' #get id from hyperlink and insert here; the code between "https://docs.google.com/spreadsheets/d/" and "/edit"
append_sheet_data(SCOPES,SPREADSHEET_ID,DATA_TO_APPEND)

  