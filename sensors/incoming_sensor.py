from runfolder_sensor import RunfolderSensor
from runfolder_client import RunfolderClient


class IncomingSensor(RunfolderSensor):

    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(IncomingSensor, self).__init__(sensor_service=sensor_service,
                                             config=config,
                                             poll_interval=poll_interval,
                                             trigger='arteria-packs.incoming_ready')
        self._logger = self._sensor_service.get_logger(__name__)
        self._infolog("__init__")
        self._client = None

    def setup(self):
        self._infolog("setup")
        try:
            self._load_config()
            client_urls = [x['url'] for x in self.config["incoming_svc_urls"]]
            # copy all further keys of every item over to self._hostconfigs
            for x in self.config["incoming_svc_urls"]:
                self._hostconfigs[x['url']] = {}
                for y in x:
                    if y != 'url':
                        self._hostconfigs[x['url']][y] = x[y]
            self._client = RunfolderClient(client_urls, self._logger)
            self._infolog("Created client: {0}".format(self._client))
        except Exception as ex:
            # TODO: It seems that st2 isn't logging the entire exception, or
            # they're not in /var/log/st2
            self._logger.error(str(ex))
        self._infolog("setup finished")

