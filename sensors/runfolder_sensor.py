from st2reactor.sensor.base import PollingSensor
import time

class RunfolderClient():

    """Queries runfolders for their state"""

    def __init__(self, hosts):
        self._hosts = hosts

    def get_available_runfolder():
        """Checks for an available runfolder on one of the monitored hosts"""
        # TODO: Get this file out of the sensor and create some tests
        # TODO: Implement
        # Go through each monitored folder on each machine in order
        #   Conditions:
        #     - Must have a file called RTAComplete.txt
        #     - Must not have an arteria processing state file, .arteria/state. 
        #       this indicates that the file is already being maintained in some workflow
        #       (the file itself and the stackstorm key/value store contain more info)
        # If a folder is ready, it is fired away to the rule engine 

        # TODO: Testing, for now, there is always a new runfolder returned
        postfix = int(time.time() * 10)
        path = "/home/stanley/arteria/tests/monitored/mon1/" + postfix
        return { "server": "art-worker", "path": path }

class RunfolderSensor(PollingSensor):

    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(RunfolderSensor, self).__init__(sensor_service=sensor_service,
                                              config=config,
                                              poll_interval=poll_interval)
        xxx
        self._logger = self._sensor_service.get_logger(__name__)

    def setup(self):
        self._logger.debug(_logmsg("Entering setup"))
        self._client = RunfolderClient()

    def poll(self):
        result = self._client.get_available_runfolder()

        if not result:
            return

        self._handle_result(result)

    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass
 
    def _logmsg(self, msg):
        return "[RunfolderSensor]" + msg

    def _handle_result(self, result):
        trigger="arteria-pack.runfolder"
        payload = {
            'server': 'art-worker',
            'timestamp': "" + time.time()  
        }

        self._sensor_service.dispatch(trigger=trigger, payload=payload)
