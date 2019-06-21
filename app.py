# coding: utf-8
import os
import yaml

import slack_api

CONFIG_PATH = "./config.yaml"


def main():

    with open(CONFIG_PATH) as f:
        config = yaml.load(stream=f, Loader=yaml.SafeLoader)

    slack = slack_api.SlackAPI(
        config["slack"][0]["oauth_access_token"],
        config["slack"][0]["bot_user_oauth_access_token"]
    )

    channel_list = slack.get_channel_list()
    member_list = slack.get_member_list()

    channel_analysis_list = []

    for channel in channel_list:
        #print("============================")
        #print(channel["id"], channel["name"])
        user_frequency_dict = {member["id"]: 0 for member in member_list}
        user_frequency_dict["OTHERS"] = 0  # add other_user etc (rss...)
        channel_message_list = slack.get_channel_message_list(channel["id"])
        #print("message num: {}".format(len(channel_message_list)))

        channel_frequency = len(channel_message_list)

        for channel_message in channel_message_list:
            if not ("user" in channel_message["message"]):
                user_frequency_dict["OTHERS"] += 1
                continue
            user_frequency_dict[channel_message["message"]["user"]] += 1

        user_frequency_sorted = sorted(user_frequency_dict.items(), key=lambda x: x[1], reverse=True)
        #print(user_frequency_sorted)

        channel_analysis = {
            "channel": channel["name"],
            "channel_frequency": channel_frequency,
            "user_frequency": user_frequency_sorted,
        }
        channel_analysis_list.append(channel_analysis)

    channel_analysis_list_sorted = sorted(channel_analysis_list, key=lambda x: x["channel_frequency"], reverse=True)

    fields_list = []
    for channel_analysis in channel_analysis_list_sorted[:5]:
        user_frequency = channel_analysis["user_frequency"]

        fields_list.append({
            "title": "1st: {}".format(channel_analysis["channel"]),
            "value": "frequency_user: {}".format()
        })

    #slack.post_message(message=channel_analysis_list)


if __name__ == "__main__":
    main()