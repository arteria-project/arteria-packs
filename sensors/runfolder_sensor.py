from st2reactor.sensor.base import PollingSensor
import syslog
#import arteria_services

# NOTE: This sensor is not in use, it is here for test purposes only.
#       Runfolders are instead monitored by dedicated services running on the workers.
class RunfolderSensor(PollingSensor):

    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(RunfolderSensor, self).__init__(sensor_service=sensor_service,
                                              config=config,
                                              poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self._infolog("__init__")

    def setup(self):
        self._infolog("setup")
        # TODO: Get the hosts from a config file
        #self._client = RunfolderClient("art-worker")
        self._infolog("setup finished")

    def poll(self):
        self._infolog("poll")

        self._infolog("Checking for available runfolders") 
        #result = self._client.get_available_runfolder()
        result = None
        self._infolog("Result from client: " + result)
        
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

    def _infolog(self, msg):
        self._logger.info("[" + self.__class__.__name__ + "] " + msg)
