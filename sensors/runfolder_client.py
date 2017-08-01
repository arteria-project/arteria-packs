import requests
import jsonpickle

print "runfolder_client module loaded"

class RunfolderClient():
    """Pulls data from all known runfolder services. If there are issues with connecting
       to any of the hosts, it will be logged but processing will continue""" 

    def __init__(self, hosts, logger):
        """Initializes the client with a list of hosts""" 
        logger.info("__init__ RunfolderClient")
        self._hosts = hosts
        self._logger = logger

    def next_ready(self):
        """Pulls the next runfolder that's ready.
           Hosts are queried in the order specified in the constructor."""
        for host in self._hosts:
            # TODO: Add packs id to log in a generic way
            self._logger.info("Querying {0}".format(host))
            url = host
            try:
                resp = requests.get(url)
                if resp.status_code != 200:
                    self._logger.error("RunfolderClient: Got status_code={0} from endpoint {1}".
                        format(resp.status_code, url))
                else:
                    json = resp.text
                    self._logger.debug("RunfolderClient: Successful call to {0}. {1}.".
                        format(url, json))
                    result = jsonpickle.decode(json)
                    return result 
            except requests.exceptions.ConnectionError:
               self._logger.error("RunfolderClient: Not able to connect to host {0}".format(host))
        return None
                

    def all_ready(self):
        """Pulls all ready runfolders, allowing the rule engine to choose between them"""
        # TODO: Implement
        pass
