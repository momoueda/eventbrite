import requests
import json
from configparser import ConfigParser

config = ConfigParser()
config.read('config.cfg')

eventbrite_token = config['user_info']['eventbrite_token']
trello_key = config['user_info']['trello_key']
trello_token = config['user_info']['trello_token']


event_id = config['site_ids']['event_id']#update event_id for each event


response = requests.get("https://www.eventbriteapi.com/v3/users/me/?token=" + eventbrite_token) #log into eventbrite

attendees = requests.get( "https://www.eventbriteapi.com/v3/events/" +event_id+ "/attendees/?token=" + eventbrite_token) #get event details
#jprint(attendees.json())

pagination = attendees.json()['pagination']
count = pagination['object_count'] #get total number of orders
print(count)




