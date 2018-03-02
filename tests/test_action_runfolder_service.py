
import mock

from st2tests.base import BaseActionTestCase

from runfolder_service import ArteriaRunfolderServiceAction

from tests.pack_test_utils import FakeResponse


class RunfolderServiceServiceTest(BaseActionTestCase):

    action_cls = ArteriaRunfolderServiceAction

    def test_get_state(self):
        expected_data = {"foo": "bar"}
        with mock.patch('requests.get',
                        return_value=FakeResponse(status_code=200, text=expected_data)) as mock_get:
            exit_flag, result = self.get_action_instance().run(cmd="get_state",
                                                               url="http://foo/")
            self.assertEqual(result, expected_data)
            self.assertTrue(exit_flag)

    def test_set_state(self):
        with mock.patch('requests.post',
                        return_value=FakeResponse(status_code=200, text="")) as mock_post:
            exit_flag = self.get_action_instance().run(cmd="set_state",
                                                       url="http://foo/",
                                                       state="done",
                                                       runfolder="my_fav_runfolder")
            self.assertTrue(exit_flag)
