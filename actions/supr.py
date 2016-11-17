#!/usr/bin/env python

import requests
import json

# Needs to be run in a Stackstorm virtualenv
from st2actions.runners.pythonrunner import Action

class Supr(Action):

    @staticmethod
    def search_by_email(base_url, email, user, key):
        search_person_url = '{}/person/search/'.format(base_url)
        # Search case insensitive
        params = {'email_i': email}
        response = requests.get(search_person_url, params=params, auth=(user, key))

        if response.status_code != 200:
            raise AssertionError("Status code returned when trying to get PI id for email: "
                                 "{} was not 200.".format(email))

        response_as_json = json.loads(response.content)
        matches = response_as_json["matches"]

        if len(matches) < 1:
            raise AssertionError("There were no hits in SUPR for email: {}".format(email))

        if len(matches) > 1:
            raise AssertionError("There we more than one hit in SUPR for email: {}".format(email))

        return matches[0]["id"]

    def run(self, action, email, supr_base_api_url, api_user, api_key):
        if action == "get_id_from_email":
            return self.search_by_email(supr_base_api_url, email, api_user, api_key)


