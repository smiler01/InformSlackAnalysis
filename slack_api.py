# coding: utf-8
import requests
import time


class SlackAPI(object):

    def __init__(self, oauth_access_token, bot_user_oauth_access_token):

        self.OAUTH_ACCESS_TOKEN = oauth_access_token
        self.BOT_USER_OAUTH_ACCESS_TOKEN = bot_user_oauth_access_token
        self.OLDEST = time.time() - 60*60*24*30

    def get_channel_list(self):

        """
        this class method is channel information getter
        :return: [{"id":aaa, "name":bbb, "members":[ccc, ddd, etc]},
                  {"id":eee, "name":fff, "members":[ggg, hhh, etc]}, ~]
        """

        url = "https://slack.com/api/channels.list"
        payload = {"token": self.BOT_USER_OAUTH_ACCESS_TOKEN}
        response = requests.get(url, params=payload)
        json_data = response.json()
        channel_list = [{"id": ch["id"], "name": ch["name"], "members": ch["members"]}
                        for ch in json_data["channels"]]

        return channel_list

    def get_channel_history(self, channel_id):

        url = "https://slack.com/api/channels.history"
        payload = {"token": self.OAUTH_ACCESS_TOKEN,
                   "channel": channel_id,
                   "oldest": "{}".format(self.OLDEST)}
        responce = requests.get(url, params=payload)
        json_data = responce.json()
        message_list = json_data["messages"]
        print(len(message_list[0]))

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
    for channel in channel_list:
        slack_api.get_channel_history(channel["id"])
        print(channel["name"])
