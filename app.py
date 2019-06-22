# coding: utf-8
import os
import copy
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

        # create member information list [{"id":***, "name":***, "frequency":***}, ...]
        member_info_list = copy.deepcopy(member_list)
        for member_info in member_info_list:
            member_info.update({"frequency": 0})
        member_info_list.append({"id": None, "name": "others", "frequency": 0})  # add "others" user

        # add member post frequency
        channel_message_list = slack.get_channel_message_list(channel["id"])
        for channel_message in channel_message_list:
            # if "user" not in message, add "others" frequency
            if not ("user" in channel_message["message"]):
                member_info_list[-1]["frequency"] += 1
                continue
            # add target-user frequency
            for member_info in member_info_list:
                if member_info["id"] == channel_message["message"]["user"]:
                    member_info["frequency"] += 1

        # sort frequency
        member_info_list_sorted = sorted(
            member_info_list, key=lambda x: x["frequency"], reverse=True)

        channel_frequency = len(channel_message_list)

        channel_analysis = {
            "channel": channel["name"],
            "channel_frequency": channel_frequency,
            "user_frequency": member_info_list_sorted,
        }
        channel_analysis_list.append(channel_analysis)

    channel_analysis_list_sorted = sorted(channel_analysis_list, key=lambda x: x["channel_frequency"], reverse=True)

    slack.post_message(message=channel_analysis_list_sorted)


if __name__ == "__main__":
    main()