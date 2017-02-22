#!/usr/bin/env python

import requests
import json
import time
from urlparse import urlparse


# Needs to be run in a Stackstorm virtualenv
from st2actions.runners.pythonrunner import Action

def rewrite_link(original_endpoint, link):
    endpoint_parsed = urlparse(original_endpoint)
    link_parsed = urlparse(link)
    return "{}://{}{}".format(endpoint_parsed.scheme,
                              endpoint_parsed.netloc,
                              link_parsed.path)

class ArteriaQuerierBase(object):

    def __init__(self, logger, sleep_time, irma_api_key):
        self.logger = logger
        self.sleep_time = sleep_time
        self.irma_api_key = irma_api_key

    def valid_status(self):
        raise NotImplementedError("Has to be implemented by inheriting class")

    def successful_status(self):
        raise NotImplementedError("Has to be implemented by inheriting class")

    def failed_status(self):
        raise NotImplementedError("Has to be implemented by inheriting class")

    def query_for_status(self, links):

        def update_links(links_results):
            for link, state in links_results.iteritems():
                if state == self.successful_status():
                    continue
                elif state in self.failed_status():
                    raise Exception("Gor a failed status from link: {}".format(link))
                elif state in self.valid_status() or not state:
                    self.logger.info('Query link: {}'.format(link))
                    response = requests.get(link, headers={'apikey': self.irma_api_key})
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
            time.sleep(self.sleep_time)
            update_links(links_results)
            self.logger.info("Updated status, now have: {}".format(links_results))

        return links_results


class ArteriaStagingQuerier(ArteriaQuerierBase):

    staging_successful = 'staging_successful'
    staging_failed = 'staging_failed'
    staging_pending = 'pending'
    staging_in_progress = 'staging_in_progress'

    def __init__(self, logger, sleep_time, irma_api_key):
        super(ArteriaStagingQuerier, self).__init__(logger, sleep_time, irma_api_key)

    def query_for_size(self, link):
        response = requests.get(link, headers={'apikey': self.irma_api_key})
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
    delivery_skipped = 'delivery_skipped'

    valid_states = [pending, mover_processing_delivery, mover_failed_delivery,
                    delivery_in_progress, delivery_successful, delivery_failed]

    successful_state = delivery_successful

    def __init__(self, logger, sleep_time, irma_api_key):
        super(ArteriaDeliveryQuerier, self).__init__(logger, sleep_time, irma_api_key)

    def successful_status(self):
        return self.successful_state

    def failed_status(self):
        return [self.mover_failed_delivery, self.delivery_failed]

    def valid_status(self):
        return self.valid_states

    def query_for_status(self, link, skip_mover):
        if skip_mover:
            self.valid_states += self.delivery_skipped
            self.successful_state = self.delivery_skipped

        while True:
            response = requests.get(link, headers={'apikey': self.irma_api_key})
            response_as_json = json.loads(response.content)
            status = response_as_json["status"]

            if status == self.successful_status():
                self.logger.info("Got successful status {}".format(status))
                return True
            elif status in self.failed_status():
                self.logger.warning("Got unsuccessful status {}".format(status))
                return False
            elif status in self.valid_status():
                self.logger.info("Got valid, but not final status, status: {}. Will keep polling.".format(status))
                # TODO Make timeout configurable
                time.sleep(5)
            else:
                self.logger.error("Got unrecognized status: {}. Will abort polling.".format(status))
                return False


class ArteriaDeliveryService(Action):

    def post_to_server(self, url, payload, irma_api_key):
        headers = {'content-type': 'application/json', 'apikey': irma_api_key}
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        if response.status_code != 202:
            raise AssertionError("Delivery server did not accept request. "
                                 "URL: {} with response: \n {}".format(url, response.content))

        response_as_json = json.loads(response.content)
        return response_as_json

    def stage_delivery(self, url, projects, irma_api_key):
        if projects:
            payload = {'projects': projects['projects']}
        else:
            payload = {}

        response = self.post_to_server(url, payload, irma_api_key)
        return response

    def deliver(self, base_url, irma_api_key, staging_id, delivery_project_id, md5sum_file, skip_mover):
        url = '{}/{}/{}'.format(base_url, 'api/1.0/deliver/stage_id', str(staging_id))
        payload = {'delivery_project_id': delivery_project_id}

        if md5sum_file:
            payload['md5sum_file'] = md5sum_file

        self.logger.debug("skip_mover was set to: {}".format(skip_mover))

        if skip_mover:
            payload['skip_mover'] = True

        response = self.post_to_server(url, payload, irma_api_key)
        link = response['delivery_order_link']
        return link

    def stage_and_check_status(self, url, irma_api_key, sleep_time, projects):
        response = self.stage_delivery(url,
                                       projects,
                                       irma_api_key)

        project_and_links = response['staging_order_links']
        self.logger.info("Projects and links was: {}".format(project_and_links))
        status_links = project_and_links.values()
        rewritten_status_links = map(lambda x: rewrite_link(url, x), status_links)

        arteria_staging_querier = ArteriaStagingQuerier(self.logger, sleep_time, irma_api_key)
        final_status = arteria_staging_querier.query_for_status(rewritten_status_links)
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

    def stage_and_check_status_of_runfolder(self, delivery_base_api_url, irma_api_key,
                                            sleep_time, runfolder_name, projects):
        url = "{}/{}/{}".format(delivery_base_api_url, 'api/1.0/stage/runfolder', runfolder_name)
        return self.stage_and_check_status(url, irma_api_key, sleep_time, projects)

    def stage_and_check_status_of_project(self, delivery_base_api_url, irma_api_key, sleep_time, project_name):
        url = "{}/{}/{}".format(delivery_base_api_url, 'api/1.0/stage/project', project_name)
        return self.stage_and_check_status(url, irma_api_key, sleep_time, projects=None)

    def run(self, action, delivery_base_api_url, irma_api_key, sleep_time, **kwargs):
        if action == "stage_runfolder":
            return self.stage_and_check_status_of_runfolder(delivery_base_api_url,
                                                            irma_api_key,
                                                            sleep_time,
                                                            kwargs['runfolder_name'],
                                                            kwargs.get('projects'))

        elif action == "stage_project":
            return self.stage_and_check_status_of_project(delivery_base_api_url,
                                                          irma_api_key,
                                                          sleep_time,
                                                          kwargs["project_name"])

        elif action == "deliver":
            status_link = self.deliver(delivery_base_api_url,
                                       irma_api_key,
                                       kwargs['staging_id'],
                                       kwargs['delivery_project_id'],
                                       kwargs.get('md5sum_file'),
                                       kwargs.get('skip_mover'))
            return True, {"project_name": kwargs["ngi_project_name"], "status_link": status_link}

        elif action == "delivery_status":
            status_endpoint = kwargs['status_link']
            arteria_delivery_querier = ArteriaDeliveryQuerier(self.logger, sleep_time, irma_api_key)
            return arteria_delivery_querier.query_for_status(status_endpoint, kwargs.get('skip_mover'))

        else:
            raise AssertionError("Action: {} was not recognized.".format(action))

