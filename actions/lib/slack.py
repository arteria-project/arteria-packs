
import requests

import datetime

from st2actions.runners.pythonrunner import Action

class SlackNotifier():

    def __init__(self, base_url, channel, user, icon_emoji=None):
        self.session = requests.Session()
        self.headers = {'content-type': 'application/json'}
        self.base_url = base_url
        self.channel = channel
        self.user = user
        if icon_emoji:
            self.icon_emoji = icon_emoji
        else:
            self.icon_emoji = ':robot_face:'

    def _post_to_slack(self, json_message):
        response = self.session.post(self.base_url, json=json_message)
        return response.status_code

    def post_message(self, message):
        json_message = {"text": message,
                        "username": self.user,
                        "icon_emoji": self.icon_emoji,
                        "mrkdwn": "true",
                        "channel": self.channel}
        return self._post_to_slack(json_message)

    def post_message_with_attachment(self, message, attachment):
        attachments = [{
            "mrkdwn_in": ["text"],
            "text": "```{}```".format(attachment)
        }]
        json_message = {"text": message,
                        "username": self.user,
                        "icon_emoji": self.icon_emoji,
                        "attachments": attachments,
                        "mrkdwn": "true",
                        "channel": self.channel}
        return self._post_to_slack(json_message)


class SlackPoster(Action):

    def run(self, channel, user, message, **kwargs):
        notifier = SlackNotifier(base_url=self.config["slack_webhook_url"],
                                 channel=channel,
                                 user=user,
                                 icon_emoji=kwargs.get('emoji_icon'))
        try:
            status = notifier.post_message(message)
            if status == 200:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error("Got error when trying to post to Slack: {}".format(e))
            return False


