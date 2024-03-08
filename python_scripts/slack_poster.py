'''
slack_poster.py

This Python code defines a class SlackPoster to interact with Slack. It provides functionality to
post messages and upload files to a specified Slack channel. The class uses the Slack API and 
requires an environment with Slack token and channel details set up.
'''

import argparse
import logging
import os
import requests

from dotenv import load_dotenv

load_dotenv()

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')

SLACK_API_URL = "https://slack.com/api/"


class SlackPoster:
    def __init__(self, log_name: str = "slack_poster"):
        self.logger = logging.getLogger(log_name)
        self.logger.addHandler(logging.NullHandler())

    def post_message_file(self, message, filepath, filename):
        """
        Post message and files on slack
        """
        try:
            url = SLACK_API_URL + "files.upload"
            data = {
                "token": SLACK_TOKEN,
                "channels": SLACK_CHANNEL,
                "title": filename,
                "initial_comment": message
            }
            files = {'file': open(filepath, 'rb')}
            result = requests.post(url, data=data, files=files)

            self.logger.info(result)

        except Exception as e:
            self.logger.error("Error uploading file: {}".format(e))

    def post_message(self, message):
        """
        Post message on slack
        """
        try:
            url = SLACK_API_URL + "/chat.postMessage"
            headers = {
                "Authorization": "Bearer " + SLACK_TOKEN
            }
            data = {
                "channel": SLACK_CHANNEL,
                'text': message,
            }
            result = requests.post(url, headers=headers, data=data)

            self.logger.info(result)

        except Exception as e:
            self.logger.error("Error uploading file: {}".format(e))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--msg", type=str,
                        help="Name", default="empty msg")
    args = parser.parse_args()

    object = SlackPoster()
    object.post_message_file(
        args.msg, "/tmp/record_screen.mp4", "movie.mp4")
    
if __name__ == "__main__":
    main()