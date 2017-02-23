#!/usr/bin/env python

import requests
import json
import time
from urlparse import urlparse


# Needs to be run in a Stackstorm virtualenv
from st2actions.runners.pythonrunner import Action


class ProjectAndStageId(object):
    staging_successful = 'staging_successful'
    staging_failed = 'staging_failed'
    staging_pending = 'pending'
    staging_in_progress = 'staging_in_progress'

    valid_states = [staging_successful, staging_failed, staging_pending, staging_in_progress]

    def __init__(self, project, stage_id, size=None, status=None):
        self.project = project
        self.stage_id = stage_id
        self.status = status
        self.size = size

    def set_status(self, new_status):
        if new_status in self.valid_states:
            self.status = new_status
        else:
            raise AssertionError("Cannot set staging status to invalid status: {}".format(new_status))

    def set_size(self, new_size):
        self.size = new_size

    def is_ready(self):
        return self.is_successful() or (self.status == self.staging_failed)

    def is_successful(self):
        return self.status == self.staging_successful


class ProjectAndDeliveryId(object):
    def __init__(self, project, delivery_id, status=None):
        self.project = project
        self.delivery_id = delivery_id
        self.status = status


class ArteriaDeliveryServiceHandler(object):

    def __init__(self, logger, delivery_service_location, irma_api_key, sleep_time):
        self.logger = logger
        self.delivery_service_location = delivery_service_location
        self.irma_api_key = irma_api_key
        self.sleep_time = sleep_time

    def _post_to_server(self, url, payload):
        headers = {'content-type': 'application/json', 'apikey': self.irma_api_key}
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        if response.status_code != 202:
            raise AssertionError("Delivery server did not accept request. "
                                 "URL: {} with response: \n {}".format(url, response.content))

        response_as_json = json.loads(response.content)
        return response_as_json

    def _get_from_server(self, url):
        response = requests.get(url, headers={'apikey': self.irma_api_key})
        if response.status_code != 200:
            raise AssertionError("Did not get 200 status back from server at url: {},"
                                 " got status: {} and response: {}".format(url, response.status_code, response.content))

        response_as_json = json.loads(response.content)
        return response_as_json

    @staticmethod
    def parse_stage_order_ids_from_response(response):
        projects_and_staging_order_ids = response['staging_order_ids']
        result = []
        for project, stage_order_id in projects_and_staging_order_ids.iteritems():
            result.append(ProjectAndStageId(project, stage_order_id))

        return result

    def stage_runfolder(self, runfolder_name, projects):
        stage_runfolder_endpoint = '{}/api/1.0/stage/runfolder/{}'.format(self.delivery_service_location, runfolder_name)

        if projects:
            payload = {'projects': projects['projects']}
        else:
            payload = {}

        response = self._post_to_server(stage_runfolder_endpoint, payload)
        return self.parse_stage_order_ids_from_response(response)

    def stage_project(self, project_name):
        stage_project_endpoint = '{}/api/1.0/stage/project/{}'.format(self.delivery_service_location, project_name)
        response = self._post_to_server(stage_project_endpoint, payload=None)
        return self.parse_stage_order_ids_from_response(response)

    def update_stage_status(self, project_and_stage_id):
        stage_status_endpoint = '{}/api/1.0/stage/{}'.format(self.delivery_service_location,
                                                             project_and_stage_id.stage_id)
        response = self._get_from_server(stage_status_endpoint)
        project_and_stage_id.set_status(response['status'])
        return project_and_stage_id

    def update_stage_size(self, project_and_stage_id):
        stage_status_endpoint = '{}/api/1.0/stage/{}'.format(self.delivery_service_location,
                                                             project_and_stage_id.stage_id)
        response = self._get_from_server(stage_status_endpoint)
        project_and_stage_id.set_size(response['size'])
        return project_and_stage_id

    def delivery(self, staging_id, skip_mover):
        deliver_status_endpoint = '{}/api/1.0/deliver/{}'.format(self.delivery_service_location, staging_id)
        pass

    def query_delivery_status(self, delivery_id):
        pass


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

    def stage_and_check_status(self, base_url, url, irma_api_key, sleep_time, projects):
        response = self.stage_delivery(url,
                                       projects,
                                       irma_api_key)

        project_and_ids = response['staging_order_ids']
        self.logger.info("Projects and status is was: {}".format(project_and_ids))
        status_links = map(lambda x: "{}/api/1.0/stage/{}".format(base_url, x), project_and_ids.values())

        arteria_staging_querier = ArteriaStagingQuerier(self.logger, sleep_time, irma_api_key)
        final_status = arteria_staging_querier.query_for_status(status_links)
        links_to_projects = {v: k for k, v in project_and_ids.iteritems()}
        self.logger.info("links to projects was: {}".format(links_to_projects))

        exit_status = True
        result = {}

        for staging_id, project in links_to_projects.iteritems():
            status = final_status[staging_id]
            if not status == arteria_staging_querier.successful_status():
                exit_status = False
                self.logger.error('Project: {} was not successfully staged. '
                                  'Had status: {}. Link was: {}'.format(project, status, staging_id))
            size = arteria_staging_querier.query_for_size(staging_id)
            # The last part of the link contains the staging id. This is sort of a hack,
            # but it will have to do for now. /JD 20161215
            result[project] = {'staging_id': int(staging_id.split('/')[-1]), 'size':  size}

        self.logger.info("Exit status was: {}, result was: {}".format(exit_status, result))
        return exit_status, result

    def stage_and_check_status_of_runfolder(self, delivery_base_api_url, irma_api_key,
                                            sleep_time, runfolder_name, projects):
        url = "{}/{}/{}".format(delivery_base_api_url, 'api/1.0/stage/runfolder', runfolder_name)
        return self.stage_and_check_status(delivery_base_api_url, url, irma_api_key, sleep_time, projects)

    def stage_and_check_status_of_project(self, delivery_base_api_url, irma_api_key, sleep_time, project_name):
        url = "{}/{}/{}".format(delivery_base_api_url, 'api/1.0/stage/project', project_name)
        return self.stage_and_check_status(delivery_base_api_url, url, irma_api_key, sleep_time, projects=None)

    def _wait_for_staging_to_finish(self, projects_and_stage_ids, arteria_delivery_service, sleep_time):
        # Keep looping until all elements are in a ready state, i.e. finished or error
        while True:
            for project_and_stage_id in projects_and_stage_ids:
                arteria_delivery_service.update_stage_status(project_and_stage_id)
                self.logger.info("Current state of project and stage id is: "
                                 "{} {} {}".format(project_and_stage_id.project,
                                                   project_and_stage_id.stage_id,
                                                   project_and_stage_id.status))

            if all(elem.is_ready() for elem in projects_and_stage_ids):
                break
            else:
                time.sleep(sleep_time)

    def _parse_projects_and_stage_ids_to_dict(self, projects_and_stage_ids, service):
        result = {}
        for project_and_stage_id in projects_and_stage_ids:
            if project_and_stage_id.is_successful():
                service.update_stage_size(project_and_stage_id)
                result[project_and_stage_id.project] = {'size': project_and_stage_id.size,
                                                        'staging_id': project_and_stage_id.stage_id,
                                                        'successful': True}
            else:
                result[project_and_stage_id.project] = {'staging_id': project_and_stage_id.stage_id,
                                                        'successful': False}
        return result

    def _await_and_parse_results(self, projects_and_stage_ids, service, sleep_time):
        self._wait_for_staging_to_finish(projects_and_stage_ids, service, sleep_time)
        result = self._parse_projects_and_stage_ids_to_dict(projects_and_stage_ids, service)
        if all(elem.is_successful() for elem in projects_and_stage_ids):
            return True, result
        else:
            return False, result

    def run(self, action, delivery_base_api_url, irma_api_key, sleep_time, **kwargs):

        service = ArteriaDeliveryServiceHandler(logger=self.logger,
                                                delivery_service_location=delivery_base_api_url,
                                                sleep_time=sleep_time,
                                                irma_api_key=irma_api_key)

        if action == "stage_runfolder":
            projects_and_stage_ids = service.stage_runfolder(runfolder_name=kwargs['runfolder_name'],
                                                             projects=kwargs['projects'])
            return self._await_and_parse_results(projects_and_stage_ids, service, sleep_time)

        elif action == "stage_project":
            projects_and_stage_ids = service.stage_project(project_name=kwargs['project_name'])
            return self._await_and_parse_results(projects_and_stage_ids, service, sleep_time)

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

