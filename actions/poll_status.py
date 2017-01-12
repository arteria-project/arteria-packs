#!/usr/bin/env python

import datetime
import time
from urlparse import urlparse

import requests

from requests.exceptions import RequestException

# Needs to be run in a Stackstorm virtualenv
from st2actions.runners.pythonrunner import Action

class PollStatus(Action):
    """
    Polls a give micro service URL for current status of some long running process.

    Will check the HTTP server's response to determine whether or not the process has finished
    processing. It expects a JSON field called "state", and will continue to poll the URL
    as long as "state" equals "started". If e.g. "done", "error", or "none" is received an
    error is generated and the polling stops.
    """

    def query(self, url, verify_ssl_cert):
        try:
            resp = requests.get(url, verify=verify_ssl_cert)
            return resp
        except RequestException as err:
            self.logger.error("An error was encountered when "
                              "querying url: {0},  {1}".format(url, err))
            raise err

    def post_to_endpoint(self, endpoint, body, irma_mode, verify_ssl_cert):

        def _rewrite_link(link):
            endpoint_parsed = urlparse(endpoint)
            # Gets the first non-empty element from the path, this lets it account
            # for multiple slashes
            first_part_of_path = filter(None, endpoint_parsed.path.split('/'))[0]
            link_parsed = urlparse(link)
            return "{}://{}/{}{}?{}".format(endpoint_parsed.scheme,
                                            endpoint_parsed.netloc,
                                            first_part_of_path,
                                            link_parsed.path,
                                            endpoint_parsed.query)

        try:
            response = requests.post(endpoint, json=body, verify=verify_ssl_cert)
            response_json = response.json()
            self.logger.info("Service accepted our request and responded with payload: {}".format(response_json))

            if irma_mode:
                modified_link = _rewrite_link(response_json['link'])
                self.logger.info("In irma mode, will rewrite link to: {}".format(modified_link))
                return modified_link
            else:
                return response_json['link']
        except RequestException as err:
            self.logger.error("An error was encountered when trying to "
                                "post to url: {0}, {1}".format(endpoint, err))
            raise err
        except KeyError as err:
            self.logger.error("Could not find correct key in response json: {}".format(response_json))
            raise err
        except ValueError as err:
            self.logger.error("Error decoding response as json. Got status: {} and response: {}".format(
                response.status_code,
                response.content))
            raise err

    def check_status(self, url, sleep, ignore_result, verify_ssl_cert, max_retries):
        """
        Query the url end-point. Can be called directly from StackStorm, or via the script cli
        :param url: to call
        :param sleep: minutes to sleep between attempts
        :param ignore_result: return 0 exit status even if polling failed (for known errors).
        :param verify_ssl_cert: Set to False to skip verifying the ssl cert when making requests
        :param max_retries: maximum number of retries
        :return: None
        """
        retry_attempts = 0
        state = "started"

        while state == "started" or state == "pending" or not state:
            current_time = datetime.datetime.now()

            resp = self.query(url, verify_ssl_cert)
            json_resp = resp.json()
            state = json_resp["state"]

            if state == "started" or state == "pending":
                self.logger.info("{0} -- {1} returned state {2}. Sleeping {3}m until retrying again...".format(current_time,
                                                                                                               url,
                                                                                                               state,
                                                                                                               sleep))
                time.sleep(sleep * 60)
            elif state == "done":
                self.logger.info("{0} -- {1} returned state {2}. Will now stop polling the status.".format(current_time,
                                                                                                           url,
                                                                                                           state))

                return True, json_resp
            elif state in ["error", "none", "cancelled"]:
                self.logger.warning("{0} -- {1} returned state {2}. Will now stop polling the status.".format(current_time,
                                                                                                              url,
                                                                                                              state))

                if ignore_result:
                    self.logger.warning("Ignoring the failed result because of override flag.")
                    return True, json_resp
                else:
                    return False, json_resp

            elif not state and retry_attempts < max_retries:
                retry_attempts += 1
                self.logger.warning("{0} -- {1} did not report state. "
                                    "Probably due to a connection error, "
                                    "will retry. Attempt {2} of {3}.".format(current_time,
                                                                             url,
                                                                             retry_attempts,
                                                                             max_retries))
                time.sleep(sleep * 60)
            else:
                self.logger.error("{0} -- {1} returned state unknown state {2}. "
                                  "Will now stop polling the status.".format(current_time, url, state))
                return False, json_resp

    def run(self, url, body, sleep, ignore_result, irma_mode, verify_ssl_cert, max_retries=3):
        status_link = self.post_to_endpoint(url, body, irma_mode, verify_ssl_cert)
        return self.check_status(status_link, sleep, ignore_result, verify_ssl_cert, max_retries)


