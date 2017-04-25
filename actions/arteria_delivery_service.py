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

    pending = 'pending'
    mover_processing_delivery = 'mover_processing_delivery'
    mover_failed_delivery = 'mover_failed_delivery'
    delivery_in_progress = 'delivery_in_progress'
    delivery_successful = 'delivery_successful'
    delivery_failed = 'delivery_failed'
    delivery_skipped = 'delivery_skipped'

    failed_states = [mover_failed_delivery, delivery_failed]
    valid_states = [pending, mover_processing_delivery, mover_failed_delivery,
                    delivery_in_progress, delivery_successful, delivery_failed]

    def __init__(self, project, delivery_id, status=None):
        self.project = project
        self.delivery_id = delivery_id
        self.status = status
        self.mover_delivery_id = None

    def set_mover_delivery_id(self, new_id):
        self.mover_delivery_id = new_id

    def set_status(self, new_status, skip_mover):
        if skip_mover:
            self.valid_states.append(self.delivery_skipped)

        if new_status in self.valid_states:
            self.status = new_status
        else:
            raise AssertionError("Cannot set delivery status to invalid status: {}".format(new_status))

    def is_in_progress(self, skip_mover):
        if skip_mover:
            return self.status == self.delivery_skipped
        else:
            return not (self.status in self.failed_states)

    def is_ready(self, skip_mover):
        return self.is_successful(skip_mover) or (self.status in self.failed_states)

    def is_successful(self, skip_mover):
        if skip_mover:
            return self.status == self.delivery_skipped
        else:
            return self.status == self.delivery_successful


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

    def stage_runfolder(self, runfolder_name, projects,restrict_to_projects):
        stage_runfolder_endpoint = '{}/api/1.0/stage/runfolder/{}'.format(self.delivery_service_location, runfolder_name)

        if restrict_to_projects == 'keep_all_projects':
            if projects:
                payload = {'projects': projects['projects']}
            else:
                payload = {}
        else:
            restrict_to_projects_list = [proj.strip() for proj in restrict_to_projects.split(",")]
            payload = {'projects':restrict_to_projects_list}

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

    def delivery(self, ngi_project_name, staging_id, delivery_project_id, md5sum_file, skip_mover):
        deliver_endpoint = '{}/api/1.0/deliver/stage_id/{}'.format(self.delivery_service_location, staging_id)

        payload = {'delivery_project_id': delivery_project_id}

        if md5sum_file:
            payload['md5sum_file'] = md5sum_file

        if skip_mover:
            payload['skip_mover'] = True

        response = self._post_to_server(deliver_endpoint, payload)
        return ProjectAndDeliveryId(delivery_id=response['delivery_order_id'], project=ngi_project_name)

    def update_delivery_status(self, project_and_delivery_id, skip_mover):
        delivery_status_endpoint = '{}/api/1.0/deliver/status/{}'.format(self.delivery_service_location,
                                                                         project_and_delivery_id.delivery_id)
        response = self._get_from_server(delivery_status_endpoint)
        project_and_delivery_id.set_status(response['status'], skip_mover)
        project_and_delivery_id.set_mover_delivery_id(response['mover_delivery_id'])
        return project_and_delivery_id


class ArteriaDeliveryService(Action):

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
                                                             projects=kwargs['projects'],
                                                             restrict_to_projects=kwargs['restrict_to_projects'])
            return self._await_and_parse_results(projects_and_stage_ids, service, sleep_time)

        elif action == "stage_project":
            projects_and_stage_ids = service.stage_project(project_name=kwargs['project_name'])
            return self._await_and_parse_results(projects_and_stage_ids, service, sleep_time)

        elif action == "deliver":
            skip_mover = kwargs.get('skip_mover')
            project_and_delivery_id = service.delivery(ngi_project_name=kwargs['ngi_project_name'],
                                                       delivery_project_id=kwargs['delivery_project_id'],
                                                       staging_id=kwargs['staging_id'],
                                                       md5sum_file=kwargs.get('md5sum_file'),
                                                       skip_mover=skip_mover)

            # Wait a short time and then try to update the status, just to
            # make sure we fail in this step if we get a failed status early.
            time.sleep(5)
            service.update_delivery_status(project_and_delivery_id, skip_mover=skip_mover)

            exit_flag = project_and_delivery_id.is_in_progress(skip_mover)

            return exit_flag, {'project_name': project_and_delivery_id.project,
                               'delivery_id': project_and_delivery_id.delivery_id}

        elif action == "delivery_status":

            project_and_delivery_id = ProjectAndDeliveryId(project=kwargs['ngi_project_name'],
                                                           delivery_id=kwargs['delivery_id'])
            skip_mover = kwargs.get('skip_mover')
            service.update_delivery_status(project_and_delivery_id, skip_mover=skip_mover)

            while True:
                service.update_delivery_status(project_and_delivery_id, skip_mover=kwargs.get('skip_mover'))
                if project_and_delivery_id.is_ready(skip_mover):
                    break
                else:
                    time.sleep(sleep_time)

            return_flag = project_and_delivery_id.is_successful(skip_mover=skip_mover)
            return return_flag, {'project_name': project_and_delivery_id.project,
                                 'status': project_and_delivery_id.status,
                                 'delivery_id': project_and_delivery_id.delivery_id,
                                 'mover_delivery_id': project_and_delivery_id.mover_delivery_id}
        else:
            raise AssertionError("Action: {} was not recognized.".format(action))

