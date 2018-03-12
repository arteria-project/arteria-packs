
import requests
import json

from st2actions.runners.pythonrunner import Action


class ArteriaRunfolderServiceAction(Action):

    GET_CMD = "get_state"
    SET_CMD = "set_state"

    COMMANDS = [GET_CMD, SET_CMD]

    def _verify_command_valid(self, cmd):
        return cmd in self.COMMANDS

    def run(self, cmd, url, runfolder=None, state=None):

        if not self._verify_command_valid(cmd):
            self.logger.error("Command: {} is not valid. Valid commands are: {}".format(cmd, self.COMMANDS))
            return False, ""

        if cmd == self.GET_CMD:
            return self.get_state(url, runfolder, state)
        else:
            return self.set_state(url, runfolder, state)

    def get_state(self, url, runfolder, state):
        if runfolder:
            get_state_url = "{}/{}/{}".format(url.strip("/"), "api/1.0/runfolders/path", runfolder.strip("/"))
            args = None
        else:
            if not state:
                state = "*"
            args = {"state": state}
            get_state_url = "{}/{}".format(url.strip("/"), "api/1.0/runfolders")

        response = requests.get(get_state_url, params=args)
        if response.status_code == 200:
            return True, json.loads(response.text)
        else:
            return False, json.loads(response.text)

    def set_state(self, url, runfolder, state):
        if not state:
            self.logger.error("You have to specify a state!")
            return False, ""

        if not runfolder:
            self.logger.error("You have to specify a runfolder!")
            return False, ""

        set_state_url = "{}/{}/{}".format(url.strip("/"), "api/1.0/runfolders/path", runfolder)
        response = requests.post(set_state_url, data=json.dumps({"state": state.lower()}))
        if response.status_code == 200:
            return True
        else:
            return False
