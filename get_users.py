from datetime import datetime, timezone
import os
import requests
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi


load_dotenv()
APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')

# Initialize API with the user access token
api = FacebookAdsApi.init(app_id=APP_ID, app_secret=APP_SECRET, access_token=PAGE_ACCESS_TOKEN)

group_id = '633519180123966'  # Replace with your group ID

url = (
    f"https://graph.facebook.com/v20.0/{group_id}/members?"
    f"fields=id,name"
    f"&access_token={PAGE_ACCESS_TOKEN}"
)

response = requests.get(url)
response_json = response.json()

if 'data' in response_json:
    members = response_json['data']
else:
    print(f"Failed to retrieve members: {response_json}")
    members = []

# Print all members
for member in members:
    print(f"Name: {member['name']}, ID: {member['id']}")

# Handle pagination if there are more members to retrieve
while 'paging' in response_json and 'next' in response_json['paging']:
    next_url = response_json['paging']['next']
    response = requests.get(next_url)
    response_json = response.json()
    
    if 'data' in response_json:
        members = response_json['data']
        for member in members:
            print(f"Name: {member['name']}, ID: {member['id']}")
    else:
        break
