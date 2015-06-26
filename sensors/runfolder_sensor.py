from st2reactor.sensor.base import PollingSensor
import syslog
from runfolder_client import RunfolderClient
import jsonpickle
import requests

class RunfolderSensor(PollingSensor):

    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(RunfolderSensor, self).__init__(sensor_service=sensor_service,
                                              config=config,
                                              poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self._infolog("__init__")

    def setup(self):
        self._infolog("setup")
        try:
            # TODO: Config, from st2
            self._client = RunfolderClient(["http://testtank1:10800"], self._logger)
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
        payload = {
            'host': result['host'],
            'runfolder': result['path'],
            'link': result['link'],
            'timestamp': '1234'
        }
        self._sensor_service.dispatch(trigger=trigger, payload=payload)

    def _infolog(self, msg):
        self._logger.info("[arteria-packs." + self.__class__.__name__ + "] " + msg)
