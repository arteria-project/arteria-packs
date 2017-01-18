#!/usr/bin/env python

import requests
import json
import time


# Needs to be run in a Stackstorm virtualenv
from st2actions.runners.pythonrunner import Action

class ArteriaQuerierBase(object):

    def __init__(self, logger):
        self.logger = logger

    def valid_status(self):
        raise NotImplementedError("Has to be implemented by inheriting class")

    def successful_status(self):
        raise NotImplementedError("Has to be implemented by inheriting class")

    def failed_status(self):
        raise NotImplementedError("Has to be implemented by inheriting class")

    def query_for_status(self, links):

        def update_links(links_results):
            for link, state in links_results.iteritems():
                if state == self.successful_status() or state in self.failed_status():
                    continue
                elif state in self.valid_status() or not state:
                    response = requests.get(link)
                    response_as_json = json.loads(response.content)
                    links_results[link] = response_as_json["status"]
                else:
                    raise NotImplementedError("Do not know how to handle state: {}".format(state))

        def is_in_end_state(link_state):
            if not link_state:
                return False
            else:
                return link_state == self.successful_status() or link_state in self.failed_status()

        links_results = dict(map(lambda x: (x, None), links))

        while not all(map(is_in_end_state, links_results.values())):
            # TODO Make sleep time configurable
            time.sleep(5)
            update_links(links_results)
            self.logger.info("Updated status, now have: {}".format(links_results))

        return links_results


class ArteriaStagingQuerier(ArteriaQuerierBase):

    staging_successful = 'staging_successful'
    staging_failed = 'staging_failed'
    staging_pending = 'pending'
    staging_in_progress = 'staging_in_progress'

    def __init__(self, logger):
        super(ArteriaStagingQuerier, self).__init__(logger)

    def query_for_size(self, link):
        response = requests.get(link)
        response_as_json = json.loads(response.content)
        return response_as_json['size']

    def successful_status(self):
        return self.staging_successful

    def failed_status(self):
        return [self.staging_failed]

    def valid_status(self):
        valid_states = [self.staging_successful, self.staging_failed, self.staging_pending, self.staging_in_progress]
        return valid_states


class ArteriaDeliveryQuerier(ArteriaQuerierBase):

    pending = 'pending'
    mover_processing_delivery = 'mover_processing_delivery'
    mover_failed_delivery = 'mover_failed_delivery'
    delivery_in_progress = 'delivery_in_progress'
    delivery_successful = 'delivery_successful'
    delivery_failed = 'delivery_failed'

    def __init__(self, logger):
        super(ArteriaDeliveryQuerier, self).__init__(logger)

    def successful_status(self):
        return self.delivery_successful

    def failed_status(self):
        return [self.mover_failed_delivery, self.delivery_failed]

    def valid_status(self):
        valid_states = [self.pending, self.mover_processing_delivery, self.mover_failed_delivery,
                        self.delivery_in_progress, self.delivery_successful, self.delivery_failed]
        return valid_states


class ArteriaDeliveryService(Action):

    def post_to_server(self, url, payload):
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        if response.status_code != 202:
            raise AssertionError("Delivery server did not accept request. "
                                 "URL: {} with response: \n {}".format(url, response.content))

        response_as_json = json.loads(response.content)
        return response_as_json

    def stage_delivery(self, url, projects):
        if projects:
            payload = {'projects': projects['projects']}
        else:
            payload = {}

        response = self.post_to_server(url, payload)
        return response

    def deliver(self, base_url, staging_id, delivery_project_id, md5sum_file):
        url = '{}/{}/{}'.format(base_url, 'api/1.0/deliver/stage_id', str(staging_id))
        payload = {'delivery_project_id': delivery_project_id}

        if md5sum_file:
            payload['md5sum_file'] = md5sum_file

        response = self.post_to_server(url, payload)
        links = response['delivery_order_link']
        return [links]

    def stage_and_check_status(self, url, projects):
        response = self.stage_delivery(url,
                                       projects)

        project_and_links = response['staging_order_links']
        self.logger.info("Projects and links was: {}".format(project_and_links))
        status_links = project_and_links.values()
        arteria_staging_querier = ArteriaStagingQuerier(self.logger)
        final_status = arteria_staging_querier.query_for_status(status_links)
        links_to_projects = {v: k for k, v in project_and_links.iteritems()}

        exit_status = True
        result = {}

        for link, project in links_to_projects.iteritems():
            status = final_status[link]
            if not status == arteria_staging_querier.successful_status():
                exit_status = False
                self.logger.error('Project: {} was not successfully staged. '
                                  'Had status: {}. Link was: {}'.format(project, status, link))
            size = arteria_staging_querier.query_for_size(link)
            # The last part of the link contains the staging id. This is sort of a hack,
            # but it will have to do for now. /JD 20161215
            result[project] = {'staging_id': int(link.split('/')[-1]), 'size':  size}

        self.logger.info("Exit status was: {}, result was: {}".format(exit_status, result))
        return exit_status, result

    def stage_and_check_status_of_runfolder(self, delivery_base_api_url, runfolder_name, projects):
        url = "{}/{}/{}".format(delivery_base_api_url, 'api/1.0/stage/runfolder', runfolder_name)
        return self.stage_and_check_status(url, projects)

    def stage_and_check_status_of_project(self, delivery_base_api_url, project_name):
        url = "{}/{}/{}".format(delivery_base_api_url, 'api/1.0/stage/project', project_name)
        return self.stage_and_check_status(url, projects=None)

    def run(self, action, delivery_base_api_url, **kwargs):
        if action == "stage_runfolder":
            return self.stage_and_check_status_of_runfolder(delivery_base_api_url,
                                                            kwargs['runfolder_name'],
                                                            kwargs.get('projects'))

        elif action == "stage_project":
            return self.stage_and_check_status_of_project(delivery_base_api_url,
                                                          kwargs["project_name"])

        elif action == "deliver":
            status_links = self.deliver(delivery_base_api_url,
                                        kwargs['staging_id'],
                                        kwargs['delivery_project_id'],
                                        kwargs.get('md5sum_file'))
            arteria_delivery_querier = ArteriaDeliveryQuerier(self.logger)
            return arteria_delivery_querier.query_for_status(status_links)
        else:
            raise AssertionError("Action: {} was not recognized.".format(action))

