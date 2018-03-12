
import json

import mock

from st2tests.base import BaseActionTestCase

from bcl2fastq_service import ArteriaBcl2FastqServiceAction

from tests.pack_test_utils import FakeResponse



class Bcl2FastqServiceTest(BaseActionTestCase):

    action_cls = ArteriaBcl2FastqServiceAction

    dummy_link_obj = {"link": "http://foo/status"}

    def test_start_command(self):
        expected_data = {"foo": "bar"}
        with mock.patch('requests.post',
                        return_value=FakeResponse(status_code=202, text=expected_data)) as mock_post:
            exit_flag, result = self.get_action_instance().run(cmd="start",
                                                               url="http://foo/",
                                                               runfolder="my_fav_runfolder")            
            self.assertTrue(exit_flag)
            self.assertEqual(result, expected_data)

    def run_with_state(self, state, expected_exit_status):
        state_obj = {"state": state }
        with mock.patch('requests.get', return_value=FakeResponse(status_code=200,
                                                                  text=state_obj)):

            exit_flag, result = self.get_action_instance().run(cmd="poll",
                                                               url="http://foo/",
                                                               runfolder="my_fav_runfolder")
            self.assertEqual(exit_flag, expected_exit_status)

    def test_poll_command_done(self):
        expected_data = {"state": "done"}
        with mock.patch('requests.get',
                        return_value=FakeResponse(status_code=200, text=expected_data)) as mock_post:
            exit_flag, result = self.get_action_instance().run(cmd="poll",
                                                               url="http://foo/",
                                                               runfolder="my_fav_runfolder")
            self.assertTrue(exit_flag)
            self.assertEqual(result, expected_data)

    def test_done(self):
        self.run_with_state(state="done", expected_exit_status=True)

    def test_error(self):
        self.run_with_state(state="error", expected_exit_status=False)

    def test_cancelled(self):
        self.run_with_state(state="cancelled", expected_exit_status=False)

    def test_none(self):
        self.run_with_state(state="none", expected_exit_status=False)

    def test_eventually_successful_request(self):
        self.run_with_state(state="done", expected_exit_status=True)
