# coding: utf-8
import requests
import json
import time


class SlackAPI(object):

    def __init__(self, oauth_access_token, bot_user_oauth_access_token):

        self.OAUTH_ACCESS_TOKEN = oauth_access_token
        self.BOT_USER_OAUTH_ACCESS_TOKEN = bot_user_oauth_access_token
        self.LATEST = time.time()
        self.OLDEST = time.time() - 60*60*24*7

    def get_member_list(self):

        url = "https://slack.com/api/users.list"
        payload = {"token": self.BOT_USER_OAUTH_ACCESS_TOKEN}
        response = requests.get(url, params=payload)
        json_data = response.json()
        member_list = [{"id": mem["id"], "name": mem["name"]} for mem in json_data["members"]]
        return member_list

    def get_channel_list(self):

        url = "https://slack.com/api/channels.list"
        payload = {"token": self.BOT_USER_OAUTH_ACCESS_TOKEN}
        response = requests.get(url, params=payload)
        json_data = response.json()
        channel_list = [{"id": ch["id"], "name": ch["name"], "members": ch["members"]} for ch in json_data["channels"]]
        return channel_list

    def get_channel_message_list(self, channel_id):

        url = "https://slack.com/api/channels.history"
        payload = {"token": self.OAUTH_ACCESS_TOKEN,
                   "channel": channel_id,
                   "count": "{}".format(1000),
                   "latest": "{}".format(self.LATEST),
                   "oldest": "{}".format(self.OLDEST)}
        response = requests.get(url, params=payload)
        json_data = response.json()
        channel_message_list = []
        for messages in json_data["messages"]:
            channel_message_list.append({
                "message": messages,
                "latest": "{}".format(self.LATEST),
                "oldest": "{}".format(self.OLDEST)
            })
        return channel_message_list

    def post_message(self, message=None, attachments=None):

        url = "	https://slack.com/api/chat.postMessage"
        payload = {
            "token": self.BOT_USER_OAUTH_ACCESS_TOKEN,
            "channel": "#bot_test",
            "text": "<!channel>\n*{}*".format(message),
            "attachments": "{}".format(attachments),
        }
        response = requests.post(url, data=payload)
        print(response)


