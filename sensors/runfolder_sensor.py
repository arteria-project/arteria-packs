from st2reactor.sensor.base import PollingSensor
from runfolder_client import RunfolderClient
from datetime import datetime
import yaml
import os

class RunfolderSensor(PollingSensor):

    def __init__(self, sensor_service, config=None, poll_interval=None, trigger='arteria.runfolder_ready'):
        super(RunfolderSensor, self).__init__(sensor_service=sensor_service,
                                              config=config,
                                              poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self._infolog("__init__")
        self._client = None
        self._trigger = trigger
        self._hostconfigs = {}

    def setup(self):
        self._infolog("setup")
        client_urls = self._config["runfolder_service_url"]
        self._client = RunfolderClient(client_urls, self._logger)
        self._infolog("Created client: {0}".format(self._client))
        self._infolog("setup finished")

    def poll(self):
        self._infolog("poll")
        self._infolog("Checking for available runfolders")
        result = self._client.next_ready()
        self._infolog("Result from client: {0}".format(result))
        if result:
            self._handle_result(result)

    def cleanup(self):
        self._infolog("cleanup")

    def add_trigger(self, trigger):
        self._infolog("add_trigger")

    def update_trigger(self, trigger):
        self._infolog("update_trigger")

    def remove_trigger(self, trigger):
        self._infolog("remove_trigger")

    def _handle_result(self, result):
        self._infolog("_handle_result")
        trigger = self._trigger
        runfolder_path = result['response']['path']
        runfolder_name = os.path.split(runfolder_path)[1]
        payload = {
            'host': result['response']['host'],
            'runfolder': runfolder_path,
            'runfolder_name': runfolder_name,
            'link': result['response']['link'],
            'timestamp': datetime.utcnow().isoformat(),
            'destination': ""
        }
        if result['requesturl'] in self._hostconfigs:
            payload['destination'] = self._hostconfigs[result['requesturl']].get('dest_folder', "")
            payload['remote_user'] = self._hostconfigs[result['requesturl']].get('remote_user', "")
            payload['user_key'] = self._hostconfigs[result['requesturl']].get('user_key', "")
        self._sensor_service.dispatch(trigger=trigger, payload=payload, trace_tag=runfolder_name)

    def _infolog(self, msg):
        self._logger.info("[arteria-packs." + self.__class__.__name__ + "] " + msg)
