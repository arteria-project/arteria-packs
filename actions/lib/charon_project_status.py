import csv
import datetime
import os
import requests
import StringIO

from st2actions.runners.pythonrunner import Action
from tabulate import tabulate

__author__ = 'Pontus'


class CharonProjects(object):

    def __init__(self, charon_base_url, charon_api_token, **filters):
        self.session = requests.Session()
        self.headers = {'X-Charon-API-token': charon_api_token, 'content-type': 'application/json'}
        self.base_url = "{}/api/v1".format(charon_base_url)
        self.filters = filters
        self.print_cols = ["projectid",
                           "sample_count",
                           "sample_count_done",
                           "sample_count_delivered"]

    def _projects(self, **local_filters):
        query_url = "{}/projects".format(self.base_url)
        json_response = self.session.get(query_url, headers=self.headers).json()
        projects = json_response.get("projects")
        filters = self.filters.copy()
        filters.update(local_filters or {})
        for key, val in filters.items():
            projects = filter(lambda prj: prj.get(key) == filters[key], projects)
        return sorted(projects, key=lambda prj: prj.get("projectid"))

    def closed(self):
        return self._projects(status="CLOSED")

    def open(self):
        return self._projects(status="OPEN")

    def pretty_print(self, projects, output_handle):
        output_handle.write(
            tabulate(
                [[project.get(col) for col in self.print_cols]
                 for project in projects],
                headers=self.print_cols))


class SlackNotifier():

    def __init__(self, base_url, channel):
        self.session = requests.Session()
        self.headers = {'content-type': 'application/json'}
        self.base_url = base_url
        self.channel = channel

    def post_message(self, message):
        attachments = [{
            "mrkdwn_in": ["text"],
            "text": "```{}```".format(message)
        }]
        json_message = {"text": "<!channel> Charon NGI-U open project status {} Z".format(datetime.datetime.utcnow().isoformat(' ')),
                        "username": "WGS status",
                        "icon_emoji": ":see_no_evil:",
                        "attachments": attachments,
                        "mrkdwn": "true",
                        "channel": self.channel}
        response = self.session.post(self.base_url, json=json_message)
        return response.status_code


class CharonProjectStatus(Action):

    def run(self):
        chcon = CharonProjects(sequencing_facility="NGI-U",
                               charon_base_url=self.config["charon_base_url"],
                               charon_api_token=self.config["charon_api_token"])
        open_projects = chcon.open()
        output_handle = StringIO.StringIO()
        chcon.pretty_print(open_projects, output_handle)
        message = output_handle.getvalue()
        try:
            sn = SlackNotifier(base_url=self.config["slack_webhook_url"],
                               channel=self.config["charon_status_report_slack_channel"])
            sn.post_message(message)
        except Exception as e:
            print("Could not post to Slack:")
            print(e.message)
        print(message)
