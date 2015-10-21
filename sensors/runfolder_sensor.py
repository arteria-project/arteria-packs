from st2reactor.sensor.base import PollingSensor
from runfolder_client import RunfolderClient
from datetime import datetime
import yaml
import os

class RunfolderSensor(PollingSensor):

    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(RunfolderSensor, self).__init__(sensor_service=sensor_service,
                                              config=config,
                                              poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self._infolog("__init__")
        self._client = None

    def setup(self):
        self._infolog("setup")
        try:
            self._load_config()
            client_urls = self.config["runfolder_svc_urls"]
            self._client = RunfolderClient(client_urls, self._logger)
            self._infolog("Created client: {0}".format(self._client))
        except Exception as ex:
            # TODO: It seems that st2 isn't logging the entire exception, or
            # they're not in /var/log/st2
            self._logger.error(str(ex))
        self._infolog("setup finished")

    def poll(self):
        try:
            self._infolog("poll")
            self._infolog("Checking for available runfolders")
            result = self._client.next_ready()
            self._infolog("Result from client: {0}".format(result))

            if result:
                self._handle_result(result)
        except Exception as ex:
            self._logger.error(str(ex))

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
        trigger = 'arteria-packs.runfolder_ready'
        runfolder_path = result['path']
        runfolder_name = os.path.split(runfolder_path)[1]
        payload = {
            'host': result['host'],
            'runfolder': runfolder_path,
            'runfolder_name': runfolder_name,
            'link': result['link'],
            'timestamp': datetime.utcnow().isoformat()
        }
        self._sensor_service.dispatch(trigger=trigger, payload=payload, trace_tag=runfolder_name)

    def _load_config(self):
        config_path = "/opt/stackstorm/packs/arteria-packs/config.yaml"
        with open(config_path) as stream:
            self.config = yaml.load(stream)
            self._infolog("Loaded configuration from {}".format(config_path))

    def _infolog(self, msg):
        self._logger.info("[arteria-packs." + self.__class__.__name__ + "] " + msg)
