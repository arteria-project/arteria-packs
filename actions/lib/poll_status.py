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


    def run(self, url, sleep, log):
        """ Our polling function that either gets called from the CLI via Click,
            or directly from Stackstorm.
        """

        state = "started"
        self.LOG_FILENAME = log

        while state == "started":
            current_time = datetime.datetime.now()

            try:
                resp = requests.get(url)
                state = resp.json()["state"]

                if state == "started":
                    self.log("{0} -- {1} returned state {2}. Sleeping {3}m until retrying again...".format(current_time, url, state, sleep))

                    time.sleep(sleep * 60)
                else:
                    self.log("{0} -- {1} returned state {2}. Will now stop polling the status.".format(current_time, url, state))

                    if state == "done":
                        self.shutdown(0)
                    elif state in ["error", "none"]:
                        self.shutdown(1)
            except RequestException as err:
                self.log("{0} -- {1} - an error was encountered: {2}".format(current_time, url, err))
                self.shutdown(1)

@click.command()
@click.option("--url", required = True, help = "URL to poll")
@click.option("--sleep", default = 1, required = False,
              help = "Number of minutes to sleep between poll (default 1)")
@click.option("--log", required = False,
              default = "/var/log/arteria/poll_status.log",
              help = "Path to log file (default /var/log/arteria/poll_status.log)")
def start(url, sleep, log):
    """ Accepts an URL to poll (e.g. http://testarteria1:10900/api/1.0/qc/status/4224)
        and sleeps a number of minutes between every poll (default 1 minute).

        Will continue to poll as long as a returned JSON field called state contains 'started'.
        Exits with an error if 'error' or 'none' is received, and with success if 'done'
        is received.
    """
    PollStatus().run(url, sleep, log)

if __name__ == "__main__":
    start()
