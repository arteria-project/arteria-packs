import unittest
import os
import shutil

class ArteriaIntegrationTest(unittest.TestCase):

    runfolder_root = "/tmp/runfolders/"
    runfolder = runfolder_root + "150204_D00458_0062_BC6L37ANXX"
    samplesheet_location = "/tmp/samplesheets"
    samplesheet = samplesheet_location + "/C6L37ANXX_samplesheet.csv"

    def setUp(self):
        # If we have for some reason poluted these folder
        # delete them now.
        if(os.path.exists(self.runfolder_root)):
            shutil.rmtree(self.runfolder_root)
        if(os.path.exists(self.samplesheet_location)):
            shutil.rmtree(self.samplesheet_location)

        #Generate runfolder and samplesheet
        os.makedirs(self.runfolder)
        os.makedirs(self.samplesheet_location)
        open(self.samplesheet, 'a').close()

    def tearDown(self):
        # Remove runfolder and samplesheet
        shutil.rmtree(self.runfolder_root)
        shutil.rmtree(self.samplesheet_location)