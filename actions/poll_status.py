#!/usr/bin/env python

import datetime
import sys
import time
import requests
from requests.exceptions import RequestException
import click
import logging
import os
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

    LOG_FILENAME = None

    def log(self, output):
        """ Quick way of putting output to a log file and stdout
        """
        logging.basicConfig(filename = self.LOG_FILENAME, level = logging.DEBUG)
        logging.debug(output)
        print output

    def shutdown(self, returncode):
        """ Shuts down the logging framework properly by flushing all buffers
            and closing handlers; then returns with a return code.
        """
        logging.shutdown()
        sys.exit(returncode)

    def query(self, url, verify_ssl_cert):
        try:
            resp = requests.get(url, verify=verify_ssl_cert)
            state = resp.json()["state"]
            return state, resp
        except RequestException as err:
            current_time = datetime.datetime.now()
            self.log("{0} -- {1} - an error was encountered: {2}".format(current_time, url, err))
            return None, None

    def run(self, url, sleep, log, ignore_result, verify_ssl_cert, max_retries = 3):
        """
        Query the url end-point. Can be called directly from StackStorm, or via the script cli
        :param url: to call
        :param sleep: minutes to sleep between attempts
        :param log: file name to write log to
        :param ignore_result: return 0 exit status even if polling failed (for known errors).
        :param verify_ssl_cert: Set to False to skip verifying the ssl cert when making requests
        :param max_retries: maximum number of retries
        :return: None
        """
        retry_attempts = 0
        state = "started"
        self.LOG_FILENAME = log

        while state == "started" or state == "pending" or not state:
            current_time = datetime.datetime.now()

            state, resp = self.query(url, verify_ssl_cert)

            if state == "started" or state == "pending":
                self.log("{0} -- {1} returned state {2}. Sleeping {3}m until retrying again...".format(current_time,
                                                                                                       url,
                                                                                                       state,
                                                                                                       sleep))
                time.sleep(sleep * 60)
            elif state == "done":
                self.log("{0} -- {1} returned state {2}. Will now stop polling the status.".format(current_time,
                                                                                                   url,
                                                                                                   state))
                self.shutdown(0)
            elif state in ["error", "none", "cancelled"]:
                self.log("{0} -- {1} returned state {2}. Will now stop polling the status.".format(current_time,
                                                                                                   url,
                                                                                                   state))
                self.log(resp.json())
                if ignore_result:
                    self.shutdown(0)
                else:
                    self.shutdown(1)

            elif not state and retry_attempts < max_retries:
                retry_attempts += 1
                self.log("{0} -- {1} did not report state. "
                         "Probably due to a connection error, will retry. Attempt {2} of {3}.".format(current_time,
                                                                                                      url,
                                                                                                      retry_attempts,
                                                                                                      max_retries))
                time.sleep(sleep * 60)
            else:
                self.log("{0} -- {1} returned state unknown state {2}. "
                         "Will now stop polling the status.".format(current_time, url, state))
                self.log(resp.json())
                self.shutdown(1)

@click.command()
@click.option("--url", required = True, help = "URL to poll")
@click.option("--sleep", default = 1, required = False,
              help = "Number of minutes to sleep between poll (default 1)")
@click.option("--log", required = False,
              default = "/var/log/arteria/poll_status.log",
              help = "Path to log file (default /var/log/arteria/poll_status.log)")
@click.option("--ignore_result", required = False,
              default = False,
              help = "Return 0 exit status even if polling failed.")
@click.option("--verify_ssl_cert/--skip_ssl_cert", required = False,
              default = True,
              help = "Verify SSL cert. Default is true.")
def start(url, sleep, log, ignore_result, verify_ssl_cert):
    """ Accepts an URL to poll (e.g. http://testarteria1:10900/api/1.0/qc/status/4224)
        and sleeps a number of minutes between every poll (default 1 minute).

        Will continue to poll as long as a returned JSON field called state contains 'started'.
        Exits with an error if 'error' or 'none' is received, and with success if 'done'
        is received.
    """
    PollStatus().run(url, sleep, log, ignore_result, verify_ssl_cert)

if __name__ == "__main__":
    start()
