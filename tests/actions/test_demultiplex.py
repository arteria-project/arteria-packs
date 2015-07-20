import unittest
import subprocess
import os
import arteria_integration_test as arteria_test


class TestDemultiplex(arteria_test.ArteriaIntegrationTest):

    def test_successful_execution(self):
        cmd = "st2 run -j arteria-packs.demultiplex " \
              "host=localhost username=vagrant password=vagrant " \
              "runfolder={0} samplesheet_location={1}".format(self.runfolder, self.samplesheet_location)

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exitcode = process.wait()

        assert(exitcode == 0)

        # Check file was copied
        target = self.runfolder + "/SampleSheet.csv"
        assert(os.path.exists(target))


if __name__ == '__main__':
    unittest.main()