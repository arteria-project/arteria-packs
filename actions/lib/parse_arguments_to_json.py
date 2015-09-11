import sys

from st2actions.runners.pythonrunner import Action

class ParseArgumentsToJson(Action):
    def _strip_null_values(self, body):
        """
        Remove any keys which have a empty value.
        :param dict: to remove from
        :return: the same dict with all empty values removed.
        """
        new_dict = {key: value for (key, value) in body.iteritems() if value}
        return new_dict

    def run(self, **kwargs):
        print(self._strip_null_values(kwargs))
