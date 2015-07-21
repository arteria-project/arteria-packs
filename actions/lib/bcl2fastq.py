#!/usr/bin/python

"""
Basic commandline parser to run bcl2fastq.
"""

import sys
import argparse
import subprocess

def main(argv):

    parser = argparse.ArgumentParser(description='Run bcl2fastq')

    # Required arguments
    parser.add_argument('--input', required=True, help='Runfolder to demultiplex (required)',)
    parser.add_argument('--output', required=True, help='Output folder for bcl2fastq (required)',)

    # Optional arguments
    parser.add_argument('--barcode_mismatches',  help='Number of mismatches to allow (0, 1 or 2)',)
    parser.add_argument('--tiles',  help='Tiles to include.',)
    parser.add_argument('--use_base_mask',  help='Base mask to use.',)
    parser.add_argument('--additional_args',  help='Additional arguments to feed to bcl2fastq',)

    args = parser.parse_args()


    commandline_collection = ["bcl2fastq",
         "--input-dir", args.input,
         "--output-dir", args.output]

    if args.barcode_mismatches:
        commandline_collection.append("--barcode-mismatches " + args.barcode_mismatches)

    if args.tiles:
        commandline_collection.append("--tiles " + args.manual_tiles)

    if args.use_base_mask:
        commandline_collection.append("--use_base_mask " + args.use_base_mask)

    if args.additional_args:
        commandline_collection.append(args.additional_args)

    # TODO Actually run bcl2fastq!
    command = " ".join(commandline_collection)
    print("Running bcl2fastq with command: " + command)

    try:
        output = subprocess.check_call(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        print("Failure in running bcl2fastq!")
        print(output.stdout)
    else:
        print("Successfully finished running bcl2fastq!")


if __name__ == "__main__":
    main(sys.argv[1:])
