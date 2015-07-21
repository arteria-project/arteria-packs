import unittest
import subprocess
import json
import arteria_integration_test as arteria_test


class TestBCL2FASTQ(arteria_test.ArteriaIntegrationTest):

    def test_successful_execution(self):
        cmd = "st2 run -j arteria-packs.bcl2fastq hosts=localhost " \
              "input={0} " \
              "output=/tmp/test hosts=localhost username=vagrant password=vagrant".format(self.runfolder)

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        exitcode = process.wait()
        assert(exitcode == 0)


if __name__ == '__main__':
    unittest.main()