#!/usr/bin/python

"""
Find and copy a samplesheet for a specific runfolder.
"""

import sys
import argparse
import os
import shutil

def main(argv):

    parser = argparse.ArgumentParser(description='Find and copy a samplesheet for a specific runfolder.')

    # Required arguments
    parser.add_argument('--runfolder', required=True, help='Runfolder to search for samplesheet for (required).')
    parser.add_argument('--samplesheet_location', required=True, help='Path where samplesheets can be found (required).')

    args = parser.parse_args()

    commandline = ["copy_samplesheet",
                   "--runfolder", args.runfolder,
                   "--samplesheet_location", args.samplesheet_location]

    runfolder_path = args.runfolder
    runfolder_dir_name = os.path.basename(runfolder_path)

    # A typical flowcell will be named in one of two ways.
    # Either: 150204_D00458_0062_BC6L37ANXX for all but MiSeq
    # Or: 130109_M00485_0028_000000000-A3349 for MiSeq.
    # The 4th field excluding the first letter (which can be
    # A or B) that denotes the machine position is the
    # name of the flowcell. # JD 20150717

    # Parse the flowcell name from the runfolder name.
    flowcell = runfolder_dir_name.split("_")[3]

    if flowcell.startswith("A") or flowcell.startswith("B"):
        flowcell = flowcell[1:]

    samplesheet = None
    # Look at samplesheet mount point for samplesheet.
    for file in os.listdir(args.samplesheet_location):
        print file
        if os.path.basename(file) == flowcell + "_samplesheet.csv":
            samplesheet = args.samplesheet_location + "/" + file

    # Copy it into the corresponding runfolder.
    if not samplesheet:
        raise IOError("Couldn't find matching samplesheet for: " + flowcell)
    else:
        samplesheet_in_runfolder_path  = runfolder_path + "/SampleSheet.csv"
        print("Attempting to copy:" +  samplesheet + " to: " + samplesheet_in_runfolder_path)
        shutil.copyfile(samplesheet, samplesheet_in_runfolder_path)
        print("Successfully copied samplesheet.")


if __name__ == "__main__":
    main(sys.argv[1:])
