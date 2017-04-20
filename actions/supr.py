#!/usr/bin/env python

import requests
import json
import math
from datetime import date
from dateutil.relativedelta import relativedelta

# Needs to be run in a Stackstorm virtualenv
from st2actions.runners.pythonrunner import Action


class Supr(Action):

    DATE_FORMAT = '%Y-%m-%d'

    @staticmethod
    def search_by_email(base_url, email, user, key):
        search_person_url = '{}/person/search/'.format(base_url)
        # Search case insensitive
        params = {'email_i': email}
        response = requests.get(search_person_url, params=params, auth=(user, key))

        if response.status_code != 200:
            raise AssertionError("Status code returned when trying to get PI id for email: "
                                 "{} was not 200. Response was: {}".format(email, response.content))

        response_as_json = json.loads(response.content)
        matches = response_as_json["matches"]

        if len(matches) < 1:
            raise AssertionError("There were no hits in SUPR for email: {}".format(email))

        if len(matches) > 1:
            raise AssertionError("There we more than one hit in SUPR for email: {}".format(email))

        return matches[0]["id"]

    @staticmethod
    def search_for_pis(project_to_email_dict, supr_base_api_url, api_user, api_key):
        res = {}
        for project, project_info in project_to_email_dict.iteritems():
            res[project] = Supr.search_by_email(base_url=supr_base_api_url,
                                                email=project_info['email'],
                                                user=api_user,
                                                key=api_key)
        return res

    @staticmethod
    def create_delivery_project(base_url, project_names_and_ids, staging_info, project_info, user, key):

        result = {}
        for ngi_project_name in staging_info.keys():
            pi_id = project_names_and_ids[ngi_project_name]

            create_delivery_project_url = '{}/ngi_delivery/project/create/'.format(base_url)

            today = date.today()
            today_formatted = today.strftime(Supr.DATE_FORMAT)
            three_months_from_now = today + relativedelta(months=+3)
            three_months_from_now_formatted = three_months_from_now.strftime(Supr.DATE_FORMAT)

            # Check smallest of delivery size in bytes and one gb (api wants size passed in giga bytes)
            size_of_delivery = max(1, math.ceil(staging_info[ngi_project_name]['size']/pow(10, 9)))

            payload = {
                'ngi_project_name': ngi_project_name,
                'title': "DELIVERY_{}_{}".format(ngi_project_name, today_formatted),
                'pi_id': pi_id,
                'start_date': today_formatted,
                'end_date': three_months_from_now_formatted,
                'continuation_name': '',
                'allocated': size_of_delivery,
                'api_opaque_data': '',
                'ngi_ready': False,
                'ngi_delivery_status': '',
                'ngi_sensitive_data': project_info[ngi_project_name]['sensitive']
            }

            response = requests.post(create_delivery_project_url,
                                     data=json.dumps(payload),
                                     auth=(user, key))

            if response.status_code != 200:
                raise AssertionError("Status code returned when trying to create delivery "
                                     "project was not 200. Response was: {}".format(response.content))

            result[ngi_project_name] = json.loads(response.content)

        return result

    @staticmethod
    def check_ngi_ready_status(supr_base_api_url, api_user, api_key, project):
        project_id = project['id']
        project_url = '{}/project/{}/'.format(supr_base_api_url, project_id)
        response = requests.get(project_url, auth=(api_user, api_key))
        response_as_json = json.loads(response.content)
        ngi_ready = response_as_json['ngi_ready']

        output_object = {project['ngi_project_name']: response_as_json['ngi_ready']}

        if ngi_ready:
            return True, output_object
        else:
            return False, output_object

    def run(self, action, supr_base_api_url, api_user, api_key, **kwargs):
        if action == "get_id_from_email":
            return self.search_for_pis(kwargs['project_to_email_sensitive_dict'], supr_base_api_url, api_user, api_key)
        elif action == 'create_delivery_project':
            return self.create_delivery_project(supr_base_api_url,
                                                kwargs['project_names_and_ids'],
                                                kwargs['staging_info'],
                                                kwargs['project_info'],
                                                api_user, api_key)
        elif action == 'check_ngi_ready':
            return self.check_ngi_ready_status(supr_base_api_url, api_user, api_key, kwargs['project'])
        else:
            raise AssertionError("Action: {} was not recognized.".format(action))

