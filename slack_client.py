from datetime import datetime, timedelta
import os
import pprint
from dotenv import load_dotenv
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()
slack_token = os.getenv('SLACK_TOKEN')
channel_id = os.getenv('CID')
playground_cid = os.getenv('PG_CID')

class SlackClient:
    def __init__(self, token, channel_id):
        self.client = WebClient(token=token)
        self.channel_id = channel_id

    def get_messages(self):
        # The API URL to fetch conversation history
        url = 'https://slack.com/api/conversations.history'

        # Parameters for the request
        params = {
            'channel': channel_id,
            'limit': 5  # Adjust the limit as needed to get more messages
        }

        # Headers for authorization
        headers = {
            'Authorization': f'Bearer {slack_token}'
        }

        # Make the request
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        pprint.pprint(data)

    def delete_message(self, message_id):
        try:
            # Call the chat.chatDelete method using the built-in WebClient
            result = self.client.chat_delete(
                channel=self.channel_id,
                ts=message_id
            )

        except SlackApiError as e:
            print(f"Error deleting message: {e}")

    def send_text_message(self, message):
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
                        
            print("Message sent successfully")
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
    
    def send_block_message(self, blocks):
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks
            )
            print("Message sent successfully")
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
