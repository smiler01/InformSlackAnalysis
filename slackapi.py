# coding: utf-8
import requests
import time
import json
from logging import getLogger
logger = getLogger(__name__)


class SlackAPI(object):

    def __init__(self, oauth_access_token=None, web_hook_url=None, day_terms=7):

        self.OAUTH_ACCESS_TOKEN = oauth_access_token
        self.WEB_HOOK_URL = web_hook_url
        self.DAY_TERMS = day_terms
        self.LATEST = time.time()
        self.OLDEST = self.LATEST - (60*60*24 * self.DAY_TERMS)

    def get_requests(self, url, data):

        try:
            response = requests.get(url, params=data)
            response.raise_for_status()
        except Exception as e:
            logger.error(e)
            return False

        json_data = response.json()
        if json_data["ok"] is not True:
            logger.error(json_data["error"])
            return False

        return json_data

    def get_users_list(self):

        url = "https://slack.com/api/users.list"
        logger.info("GET USERS_LIST: {}".format(url))
        payload = {"token": self.OAUTH_ACCESS_TOKEN}

        return self.get_requests(url, payload)

    def get_channels_list(self):

        url = "https://slack.com/api/channels.list"
        logger.info("GET CHANNELS_LIST {}".format(url))
        payload = {"token": self.OAUTH_ACCESS_TOKEN}

        return self.get_requests(url, payload)

    def get_channels_history(self, channel_id):

        url = "https://slack.com/api/channels.history"
        logger.info("GET CHANNELS_HISTORY: {}".format(url))
        payload = {"token": self.OAUTH_ACCESS_TOKEN,
                   "channel": channel_id,
                   "count": "{}".format(1000)}
                   #"latest": "{}".format(self.LATEST),
                   #"oldest": "{}".format(self.OLDEST)}

        return self.get_requests(url, payload)

    def post_message(self, message=None, attachments=None):

        payload = {'text': '<!channel>\n*{}*'.format(message),
                   'attachments': attachments}
        logger.info("POST MESSAGE")

        try:
            response = requests.post(self.WEB_HOOK_URL, data=json.dumps(payload))
            response.raise_for_status()
        except Exception as e:
            logger.error(e)
            return False

        return True
