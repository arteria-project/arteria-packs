import unittest
from mock import MagicMock
from runfolder_client import RunfolderClient

class RunfolderClientTest(unittest.TestCase):

    def test_server_down_only_logs(self):
        logger = MagicMock()
        client = RunfolderClient(["http://testarteria1-notavailable:10800"], logger)
        result = client.next_ready()
        self.assertEqual(result, None)

    def test_can_get_next(self):
        # TODO: These integration tests are semi-manual, as they expect certain data
        logger = MagicMock()
        client = RunfolderClient(["http://testarteria1:10800"], logger)
        result = client.next_ready()
        self.assertNotEqual(result, None)
        self.assertTrue('path' in result)
        self.assertTrue('host' in result)
        self.assertTrue('link' in result)
        self.assertTrue('state' in result)
        self.assertEqual(result['state'], 'ready')


if __name__ == "__main__":
    unittest.main()
