import mock
import json
import requests

from st2tests.base import BaseActionTestCase

from poll_status import PollStatus


class PollStatusTestCase(BaseActionTestCase):
    action_cls = PollStatus

    class MockPostResponse:
        def __init__(self, response_link):
            self.response_link = response_link

        def json(self):
            return {'link': self.response_link}

    class MockStatusResponse:
        def __init__(self, state_list):
            self.state_list = state_list

        # Every time we get new json, pop it from the beginning
        # of the list. This way we can vary state over time.
        def json(self):
            return {"state": self.state_list.pop(0)}

    def run_with_state(self, post_state, state, expected_exit_status, ignore_results=False):

        fake_url = 'http://foo.bar/post'
        fake_body = {'foo': 'bar'}
        response_link = 'http://foo.bar/status/'

        with mock.patch.object(requests, 'get', return_value=self.MockStatusResponse(state)) as get_mock, \
                mock.patch.object(requests, 'post', return_value=self.MockPostResponse(response_link)) as post_mock:

            action = self.get_action_instance()

            (exit_code, result) = action.run(url=fake_url,
                                             body=fake_body,
                                             sleep=0.001,
                                             ignore_result=ignore_results,
                                             verify_ssl_cert=False,
                                             irma_mode=False,
                                             max_retries=1)

            post_mock.assert_called_with(fake_url, json=fake_body, verify=False)
            get_mock.assert_called_with(response_link, verify=False)

            self.assertTrue(exit_code == expected_exit_status)

    dummy_link_obj = {'link': 'http://status.url/something'}

    def test_done(self):
        self.run_with_state(post_state=[self.dummy_link_obj], state=["done"],
                            expected_exit_status=True, ignore_results=False)

    def test_error(self):
        self.run_with_state(post_state=[self.dummy_link_obj], state=["error"],
                            expected_exit_status=False, ignore_results=False)

    def test_error_ignore_result(self):
        self.run_with_state(post_state=[self.dummy_link_obj], state=["error"],
                            expected_exit_status=True, ignore_results=True)

    def test_pending_then_done(self):
        self.run_with_state(post_state=[self.dummy_link_obj], state=["pending", "done"],
                            expected_exit_status=True, ignore_results=False)

    def test_cancelled(self):
        self.run_with_state(post_state=[self.dummy_link_obj], state=["cancelled"],
                            expected_exit_status=False, ignore_results=False)

    def test_none(self):
        self.run_with_state(post_state=[self.dummy_link_obj], state=["none"],
                            expected_exit_status=False, ignore_results=False)

    def test_eventually_successful_request(self):
        self.run_with_state(post_state=[self.dummy_link_obj], state=[None, "done"],
                            expected_exit_status=True, ignore_results=False)

