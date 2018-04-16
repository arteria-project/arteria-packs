import mock

from st2tests.base import BaseSensorTestCase

from runfolder_sensor import RunfolderSensor

from tests.pack_test_utils import  FakeResponse

class RunfolderSensorSensorTest(BaseSensorTestCase):
    sensor_cls = RunfolderSensor

    def test_method(self):
        runfolder_service_response = {"host": "4446cc6b4eff",
                                      "link": "http://runfolder-service/api/1.0/runfolders/path/opt/monitored-folder/150605_M00485_0183_000000000-ABGT6_testbio14",
                                      "path": "/opt/monitored-folder/150605_M00485_0183_000000000-ABGT6_testbio14",
                                      "service_version": "1.0.1",
                                      "state": "ready"}

        with mock.patch('requests.get', return_value=FakeResponse(status_code=200,
                                                                  text=runfolder_service_response)):
            sensor = self.get_sensor_instance(config={'runfolder_service_url': ['http://bar']})
            sensor.setup()
            sensor.poll()
            # ...

            self.assertEqual(len(self.get_dispatched_triggers()), 1)
            self.assertTriggerDispatched(trigger='arteria.runfolder_ready')