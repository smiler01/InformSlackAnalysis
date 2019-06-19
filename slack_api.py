# coding: utf-8
import requests
import time


class SlackAPI(object):

    def __init__(self, oauth_access_token, bot_user_oauth_access_token):

        self.OAUTH_ACCESS_TOKEN = oauth_access_token
        self.BOT_USER_OAUTH_ACCESS_TOKEN = bot_user_oauth_access_token
        self.LATEST = time.time()
        self.OLDEST = time.time() - 60*60*24*30

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

    def get_channel_message_list(self, channel_id, channel_name):

        url = "https://slack.com/api/channels.history"
        payload = {"token": self.OAUTH_ACCESS_TOKEN,
                   "channel": channel_id,
                   "count": "{}".format(1000)}
                   #"latest": "{}".format(self.LATEST),
                   #"oldest": "{}".format(self.OLDEST)}
        response = requests.get(url, params=payload)
        json_data = response.json()
        channel_message_list = []
        for messages in json_data["messages"]:
            channel_message_list.append({
                "id": channel_id,
                "name": channel_name,
                "message": messages
            })
        return channel_message_list


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
        print("============================")
        print(channel["id"], channel["name"])
        user_frequency_dict = {member["id"]: 0 for member in member_list}
        user_frequency_dict["OTHERS"] = 0  # add other_user etc (rss...)
        channel_message_list = slack_api.get_channel_message_list(
            channel["id"], channel["name"])
        print("message num: {}".format(len(channel_message_list)))

        for channel_message in channel_message_list:
            if not ("user" in channel_message["message"]):
                user_frequency_dict["OTHERS"] += 1
                continue
            user_frequency_dict[channel_message["message"]["user"]] += 1

        print(user_frequency_dict)

        """
        for channel_message in channel_message_list:
            for member in channel["members"]:
                print(member)

            #print(channel_message["message"])
            print("type", channel_message["message"]["type"])
            #if not ("subtype" in channel_message["message"]):
            #    continue
            #print("  subtype", channel_message["message"]["subtype"])
            if not ("user" in channel_message["message"]):
                print("    user {}".format("bot"))
                continue
            print("    user", channel_message["message"]["user"])
            """

