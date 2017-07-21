import requests
import jsonpickle


class IncomingClient:

    def __init__(self, hosts, logger):
        logger.info("__init__ IncomingClient")
        self._hosts = hosts
        self._logger = logger

    def next_ready(self):
        """Pulls the next runfolder that's ready.
           Hosts are queried in the order specified in the constructor."""
        for host in self._hosts:
            # TODO: Add packs id to log in a generic way
            self._logger.info("IncomingClient: Querying {0}".format(host))
            url = "{0}/api/1.0/runfolders/next".format(host)
            try:
                resp = requests.get(url)
                if resp.status_code != 200:
                    self._logger.error("IncomingClient: Got status_code={0} from endpoint {1}".
                                       format(resp.status_code, url))
                else:
                    json = resp.text
                    self._logger.debug("IncomingClient: Successful call to {0}. {1}.".
                                       format(url, json))
                    result = jsonpickle.decode(json)
                    return result
            except requests.exceptions.ConnectionError:
                self._logger.error("IncomingClient: Not able to connect to host {0}".format(host))
        return None
