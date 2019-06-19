# coding: utf-8
import requests
import time


class SlackAPI(object):

    def __init__(self, oauth_access_token, bot_user_oauth_access_token):

        self.OAUTH_ACCESS_TOKEN = oauth_access_token
        self.BOT_USER_OAUTH_ACCESS_TOKEN = bot_user_oauth_access_token
        self.OLDEST = time.time() - 60*60*24*30

    def get_member_list(self):

        url = "https://slack.com/api/users.list"
        payload = {"token": self.BOT_USER_OAUTH_ACCESS_TOKEN}
        response = requests.get(url, params=payload)
        json_data = response.json()
        member_list = [[{"id": mem["id"], "name": mem["name"]}] for mem in json_data["members"]]
        return member_list

    def get_channel_list(self):

        url = "https://slack.com/api/channels.list"
        payload = {"token": self.BOT_USER_OAUTH_ACCESS_TOKEN}
        response = requests.get(url, params=payload)
        json_data = response.json()
        channel_list = [{"id": ch["id"], "name": ch["name"], "members": ch["members"]} for ch in json_data["channels"]]
        return channel_list

    def get_channel_history_list(self, channel_id, channel_name):

        url = "https://slack.com/api/channels.history"
        payload = {"token": self.OAUTH_ACCESS_TOKEN,
                   "channel": channel_id,
                   "oldest": "{}".format(self.OLDEST)}
        response = requests.get(url, params=payload)
        json_data = response.json()
        channel_history_list = []
        for message in json_data["messages"]:
            channel_history_list = [{
                "id": channel_id,
                "name": channel_name,
                "history": message
            }]
        return channel_history_list


if __name__ == "__main__":

    import yaml
    CONFIG_PATH = "./config.yaml"
    with open(CONFIG_PATH) as f:
        config = yaml.load(stream=f, Loader=yaml.SafeLoader)

    slack_api = SlackAPI(
        config["slack"][0]["oauth_access_token"],
        config["slack"][0]["bot_user_oauth_access_token"]
    )

    channel_list = slack_api.get_channel_list()
    member_list = slack_api.get_member_list()

    for channel in channel_list:
        channel_history_list = slack_api.get_channel_history_list(channel["id"], channel["name"])

        for channel_history in channel_history_list:
            print(channel_history)
            """
            for message in channel_history["history"]:
                print(message)
            """

