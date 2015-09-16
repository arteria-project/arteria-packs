import sys

from st2actions.runners.pythonrunner import Action

class GetPackConfig(Action):
    """
    Used to access the config file.
    """

    def run(self, **kwargs):
        return self.config

