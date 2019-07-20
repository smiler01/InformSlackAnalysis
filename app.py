# coding: utf-8
import copy
import yaml
import logging.config
import settings
from slackapi import SlackAPI

LOGGING_CONF_PATH = "./log/debug.conf"
logging.config.fileConfig(LOGGING_CONF_PATH)
logger = logging.getLogger()

CONFIG_PATH = "./config.yaml"
with open(CONFIG_PATH) as f:
    config = yaml.load(stream=f, Loader=yaml.SafeLoader)


def format_user_ranking_attachments(users_dict):

    attachment = {"fallback": "This is slack user frequency"}

    pretext = {"pretext": ":black_small_square:*最も投稿頻度の高いユーザーです*"}
    attachment.update(pretext)

    fields = {"fields": []}
    for rank, (user_id, user_value) in enumerate(users_dict):
        fields["fields"].append(
            {"value": "{}. {}: {} messages".format(rank + 1, user_value["name"], user_value["frequency"])})
        if rank + 1 == config["displayed_number"]:
            break

    attachment.update(fields)

    return attachment


def format_channel_ranking_attachments(channels_dict):

    attachment_list = []

    attachment = {"fallback": "This is channel frequency"}
    pretext = {"pretext": ":black_small_square:*最も投稿頻度の高いチャンネルです*"}
    attachment.update(pretext)
    #attachment_list.append(attachment)

    for channel_rank, (channel_id, channel_value) in enumerate(channels_dict):

        # はじめのattachmentは上記のループ外のpretextと連動させることで、
        # 空白行を埋めることができる。attachment_list.append()をコメントアウトしているのもそれに起因
        if channel_rank != 0:
            attachment = {"fallback": "This is channel frequency"}

        fields = {"fields": []}
        fields["fields"].append(
            {"value": "{}. {}: {} messages".format(
                channel_rank + 1, channel_value["name"], channel_value["frequency"])})

        for user_rank, (user_id, user_value) in enumerate(channel_value["users"]):
            fields["fields"].append(
                {"value": "・ {}: {} messages".format(user_value["name"], user_value["frequency"])})
            if user_rank + 1 == config["displayed_number"]:
                break

        attachment.update(fields)
        attachment_list.append(attachment)

        if channel_rank + 1 == config["displayed_number"]:
            break

    return attachment_list


def main():

    slack = SlackAPI(
        oauth_access_token=settings.OAUTH_ACCESS_TOKEN,
        web_hook_url=settings.WEB_HOOK_URL,
        day_terms=config["day_terms"]
    )

    response = slack.get_users_list()
    if response is False:
        return False
    user_dict_source = response["members"]
    user_dict = {}
    for user in user_dict_source:
        if (user["deleted"] is False) and (user["is_bot"] is False):
            user_dict.update({user["id"]: {"name": user["name"], "frequency": 0}})

    response = slack.get_channels_list()
    if response is False:
        return False
    channel_dict_source = response["channels"]
    channel_dict = {}
    for channel in channel_dict_source:
        if (channel["is_archived"] is False) and (channel["is_private"] is False):
            channel_dict.update(
                {channel["id"]: {"name": channel["name"], "frequency": 0, "users": copy.deepcopy(user_dict)}})

    for channel_id, channel_value in channel_dict.items():

        response = slack.get_channels_history(channel_id)
        messages = response["messages"]

        for message in messages:

            channel_users = channel_value["users"]

            if "user" in message:
                message_user_id = message["user"]
                channel_users[message_user_id]["frequency"] += 1
                user_dict[message_user_id]["frequency"] += 1

        channel_value["users"] = sorted(channel_value["users"].items(), key=lambda x: x[1]["frequency"], reverse=True)
        channel_value["frequency"] = len(messages)

    channel_dict_desc = sorted(channel_dict.items(), key=lambda x: x[1]["frequency"], reverse=True)
    user_dict_desc = sorted(user_dict.items(), key=lambda x: x[1]["frequency"], reverse=True)

    message = ":looking: 先週のSlack内の活動頻度をお届けします"
    attachments = []
    attachment = format_user_ranking_attachments(user_dict_desc)
    attachments.append(attachment)
    attachment_list = format_channel_ranking_attachments(channel_dict_desc)
    attachments.extend(attachment_list)

    slack.post_message(message=message, attachments=attachments)


if __name__ == "__main__":
    main()
