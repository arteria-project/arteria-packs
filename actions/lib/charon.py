
import requests
import json

from st2actions.runners.pythonrunner import Action


class CharonException(Exception):
    pass


class Charon(object):

    def __init__(self, charon_base_url, charon_api_token):
        self.headers = {'X-Charon-API-token': charon_api_token, 'content-type': 'application/json'}
        self.base_url = "{}/api/v1".format(charon_base_url)

    def set_delivery_status(self, status, proj, sample):
        url = '/'.join([self.base_url, 'sample', proj, sample])
        payload = {'delivery_status': status}
        response = requests.put(url, data=json.dumps(payload), headers=self.headers)
        if not response.status_code == 204:
            raise CharonException("Charon refused request to set delivery status of {}:{} to "
                                  "DELIVERED.")


class CharonSetDeliveryStatus(Action):

    def run(self, action, **kwargs):

        if action == "set_delivery_status":
            project = kwargs["project"]
            samples = kwargs["samples"]
            delivery_status = kwargs["delivery_status"]
            charon = Charon(self.config["charon_base_url"],
                            self.config["charon_api_token"])
            for sample in samples:
                self.logger.info("Setting status of {}:{} to {}".format(project, sample, delivery_status))
                charon.set_delivery_status(delivery_status, project, sample)

        else:
            raise Exception("Does not recognize command: {}".format(action))
