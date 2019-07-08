# coding: utf-8
import copy
import yaml
import time
from datetime import datetime

import slack_api

CONFIG_PATH = "./config.yaml"
with open(CONFIG_PATH) as f:
    config = yaml.load(stream=f, Loader=yaml.SafeLoader)


def get_slack_analytics(order=1, channel_upper_limit=5, user_upper_limit=5):

    """
    :param order: 0(ascending) or 1(descending). If order =! 0 or 1, define order == 1.
    :param channel_upper_limit: Number of channel information to acquire.
    :param user_upper_limit: Number of user information to acquire.
    :return: slack analytics of JSON format.
    """

    if order == 0:
        order = False
    elif order == 1:
        order = True
    else:
        order = True

    slack = slack_api.SlackAPI(
        config["slack"]["oauth_access_token"],
        config["slack"]["bot_user_oauth_access_token"])

    channel_list = slack.get_channel_list()
    member_list = slack.get_member_list()

    channel_analysis_list = []
    for channel in channel_list:

        # create member information list [{"id":***, "name":***, "frequency":***}, ...]
        member_info_list = copy.deepcopy(member_list)
        for member_info in member_info_list:
            member_info.update({"frequency": 0})
        member_info_list.append({"id": None, "name": "others", "frequency": 0})  # add "others" user

        # add member user-post frequency
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

        # sort user-post frequency
        member_info_list_sorted = sorted(
            member_info_list, key=lambda x: x["frequency"], reverse=order)

        # mod channel_upper_limit
        if len(member_info_list_sorted) < user_upper_limit:
            user_upper_limit = len(member_info_list_sorted)
        member_info_list_sorted = member_info_list_sorted[:user_upper_limit]

        # get channel-frequency
        channel_frequency = len(channel_message_list)

        channel_analysis = {
            "channel": channel["name"],
            "channel_id": channel["id"],
            "channel_frequency": channel_frequency,
            "user_frequency": member_info_list_sorted}
        channel_analysis_list.append(channel_analysis)

    channel_analysis_list_sorted = sorted(channel_analysis_list, key=lambda x: x["channel_frequency"], reverse=order)

    if len(channel_analysis_list_sorted) < channel_upper_limit:
        channel_upper_limit = len(channel_analysis_list_sorted)

    return channel_analysis_list_sorted[:channel_upper_limit]


def get_yesterday_datetime():

    yesterday_timestamp = time.time() - 60*60*24
    yesterday_datetime = datetime.fromtimestamp(yesterday_timestamp)
    return "{0:%Y/%m/%d}".format(yesterday_datetime)


def format_attachments(slack_analysis_information):

    attachments = []

    for num, slack_analysis in enumerate(slack_analysis_information):

        attachment = {
            "fallback": "This is rss reviews attachments",
        }

        pretext_field = {"pretext": "*{}. <#{}|{}> : {} messages*".format(
            num+1, slack_analysis["channel_id"], slack_analysis["channel"],
            slack_analysis["channel_frequency"])}
        attachment.update(pretext_field)

        fields_dict = {"fields": []}
        for n, user_frequency in enumerate(slack_analysis["user_frequency"]):
            fields_dict["fields"].append({"value": "{}. {}: {} message".format(
                n+1, user_frequency["name"], user_frequency["frequency"]), "short": "true"})

        attachment.update(fields_dict)

        attachments.append(attachment)

    return attachments


def main():

    slack = slack_api.SlackAPI(
        config["slack"]["oauth_access_token"],
        config["slack"]["bot_user_oauth_access_token"])

    slack_analysis_infomation = get_slack_analytics()
    attachments = format_attachments(slack_analysis_infomation)

    message = "{}（昨日）のSlack内のアナリティクス情報をお届けします".format(get_yesterday_datetime())

    slack.post_message(message=message, attachments=attachments)


if __name__ == "__main__":
    main()
