import mock
import json
import requests

from st2tests.base import BaseActionTestCase

from poll_status import PollStatus


class PollStatusTestCase(BaseActionTestCase):
    action_cls = PollStatus

    class MockResponse:
        def __init__(self, state_list):
            self.state_list = state_list

        # Every time we get new json, pop it from the beginning
        # of the list. This way we can vary state over time.
        def json(self):
            return {"state": self.state_list.pop(0)}

    def run_with_state(self, state, expected_exit_status, ignore_results=False):
        with mock.patch.object(requests, 'get', return_value=self.MockResponse(state)):
            action = self.get_action_instance()

            (exit_code, result) = action.run(url='http://www.google.com',
                                             sleep=0.02,
                                             ignore_result=ignore_results,
                                             verify_ssl_cert=False,
                                             max_retries=1)
            self.assertTrue(exit_code == expected_exit_status)

    def test_done(self):
        self.run_with_state(state=["done"], expected_exit_status=True, ignore_results=False)

    def test_error(self):
        self.run_with_state(state=["error"], expected_exit_status=False, ignore_results=False)

    def test_error_ignore_result(self):
        self.run_with_state(state=["error"], expected_exit_status=True, ignore_results=True)

    def test_pending_then_done(self):
        self.run_with_state(state=["pending", "done"], expected_exit_status=True, ignore_results=False)

    def test_cancelled(self):
        self.run_with_state(state=["cancelled"], expected_exit_status=False, ignore_results=False)

    def test_none(self):
        self.run_with_state(state=["none"], expected_exit_status=False, ignore_results=False)

    def test_eventually_successful_request(self):
        self.run_with_state(state=[None, "done"], expected_exit_status=True, ignore_results=False)

