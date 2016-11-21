#!/usr/bin/env python

import requests
import json
import time


# Needs to be run in a Stackstorm virtualenv
from st2actions.runners.pythonrunner import Action


class ArteriaDeliveryService(Action):

    def query_for_status(self, links):
        STAGING_SUCCESSFUL = 'staging_successful'
        STAGING_FAILED = 'staging_failed'

        def update_links(links_results):
            for link, state in links_results.iteritems():
                if state == STAGING_SUCCESSFUL or state == STAGING_FAILED:
                    continue
                else:
                    response = requests.get(link)
                    response_as_json = json.loads(response.content)
                    links_results[link] = response_as_json["status"]

        def is_in_end_state(link_state):
            if not link_state:
                return False
            else:
                return link_state == STAGING_SUCCESSFUL or link_state == STAGING_FAILED

        links_results = dict(map(lambda x: (x, None), links))

        while not all(map(is_in_end_state, links_results.values())):
            # TODO Make sleep time configurable
            time.sleep(5)
            update_links(links_results)
            self.logger.info("Updated status, now have: {}".format(links_results))

        return links_results

    def stage_delivery(self, base_url, runfolder_name, projects):
        url = "{}/{}/{}".format(base_url, 'api/1.0/stage/runfolder', runfolder_name)

        if projects:
            payload = {'projects': projects['projects']}
        else:
            payload = {}
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        if response.status_code != 202:
            raise AssertionError("Delivery server did not accept staging request. "
                                 "URL: {} with response: \n {}".format(url, response.content))

        response_as_json = json.loads(response.content)

        links = response_as_json['staging_order_links']
        return links

    def run(self, action, delivery_base_api_url, **kwargs):
        if action == "stage_runfolder":
            status_links = self.stage_delivery(delivery_base_api_url, kwargs['runfolder_name'], kwargs.get('projects'))
            return self.query_for_status(status_links)
        else:
            raise AssertionError("Action: {} was not recognized.".format(action))

