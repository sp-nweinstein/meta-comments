from datetime import datetime, timedelta, timezone
import json
import os
import pprint
from tokenize import Comment

from dotenv import load_dotenv
import requests
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.business import Business
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.pagepost import PagePost
from facebook_business.api import FacebookAdsApi

from slack_client import SlackClient

load_dotenv()
APP_ID = os.getenv('APP_ID')
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
APP_SECRET = os.getenv('APP_SECRET')
QUANTIFY_AD_ACCT_ID = os.getenv('QUANTIFY_AD_ACCT_ID')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')
CID = os.getenv('CID')
PG_ID = os.getenv('PG_CID')




# Initialize API with the user access token
api = FacebookAdsApi.init(app_id=APP_ID, app_secret=APP_SECRET, access_token=PAGE_ACCESS_TOKEN)

last_week = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')


ad_account = AdAccount(QUANTIFY_AD_ACCT_ID, api=api)
# Fetch all ads under the ad account from the last 7 days
ads = ad_account.get_ads(params={
    'fields': ['id', 'name', 'adcreatives'],
    'time_range': {
        'since': yesterday,
        'until': today
    },
    'limit': 5
})

all_comment_data = []
yesterdays_comments = []

for ad in ads:
    ad_id = ad['id']

    url = (
        f"https://graph.facebook.com/v20.0/{ad_id}?"
        f"fields=creative.fields(effective_object_story_id),"
        f"insights.fields(actions)"
        f"&limit=1"
        f"&access_token={PAGE_ACCESS_TOKEN}"
    )

    response = requests.get(url)
    response_json = response.json()

    effective_object_story_id = response_json['creative']['effective_object_story_id']

    url = (
        f"https://graph.facebook.com/v20.0/{effective_object_story_id}/"
        f"comments?fields=message,created_time"
        f"&access_token={PAGE_ACCESS_TOKEN}"
    )

    response = requests.get(url)
    comments_json = response.json()



    # Calculate yesterday's date range
    yesterday_start = (datetime.now(timezone.utc) - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday_start + timedelta(hours=23, minutes=59, seconds=59)


    if 'data' in comments_json:
        for comment in comments_json['data']:
            comment_info = {
                'message': comment.get('message'),
                'created_time': comment.get('created_time'),
                'url': f"https://www.facebook.com/{effective_object_story_id}" if effective_object_story_id else None
            }
            all_comment_data.append(comment_info)

            # Convert the created_time to a datetime object
            comment_time = datetime.strptime(comment_info['created_time'], '%Y-%m-%dT%H:%M:%S%z')

            print(comment_info)
            # Check if the comment was created within yesterday's range
            if yesterday_start <= comment_time <= yesterday_end:
                yesterdays_comments.append(comment_info)


print(f"YESTERDAY'S COMMENTS: {yesterdays_comments}")

# Prepare Slack blocks for yesterday's comments
blocks = []

for comment in yesterdays_comments:
    block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Message:* {comment['message']}\n*URL:* <{comment['url']}>\n*Time:* {comment['created_time']}"
        }
    }
    blocks.append(block)

# Add a divider block between each comment
formatted_blocks = []
for block in blocks:
    formatted_blocks.append(block)
    formatted_blocks.append({"type": "divider"})

# Remove the last divider
if formatted_blocks:
    formatted_blocks.pop()


slack_client = SlackClient(token=SLACK_TOKEN, channel_id=PG_ID)

# Send the comments as a Slack block message
if formatted_blocks:
    slack_client.send_block_message(formatted_blocks)
else:
    print("No comments to send.")






