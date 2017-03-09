from st2actions.runners.pythonrunner import Action

from clarity_ext.context import ExtensionContext
from genologics.lims import *
from genologics.config import BASEURI, USERNAME, PASSWORD

import os
from tempfile import mkdtemp

class DownloadSamplesheetClarity(Action):
    """
    Downloads a samplesheet from Clarity LIMS (instead of Hermes)
    keyed on the flowcell id.
    """

    def get_processes(self, containers):
        for container in containers:
            placement = container.get_placements()
            artifact = placement[placement.keys()[0]]
            yield artifact.parent_process.id

    def highest_id(self, process_ids):
        highest_proc_number = 0
        highest_proc_type = ''
        for id in process_ids:
            (proc_type, proc_number) = id.split('-')
            if highest_proc_number == 0 or int(proc_number) > highest_proc_number:
                highest_proc_number = int(proc_number)
                highest_proc_type = proc_type
        return highest_proc_type + '-' + str(highest_proc_number)


    def run(self, flowcell_name):
        lims = Lims(BASEURI, USERNAME, PASSWORD) #Need credentials on stackstorm server for genologics package.
        containers = lims.get_containers(name=flowcell_name)
        processes = list(self.get_processes(containers))
        newest_process_id = self.highest_id(processes)
        context = ExtensionContext.create(newest_process_id)
        cwd = os.getcwd()
        try:
            #generate a fresh temp directory to mimic LIMS behaviour (avoid overwriting samplesheets)
            temp_wd = mkdtemp()
            os.chdir(temp_wd)
            samplesheet_file = context.local_shared_file("Sample Sheet")
            samplesheet = samplesheet_file.read()
            os.chdir(cwd)

        except IOError as err:
            self.logger.error('IOError while attempting to read samplesheet: {}'.format(err.message))
            raise err

        return (True, samplesheet)

