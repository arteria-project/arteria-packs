#!/usr/bin/python

"""
Basic commandline parser to run bcl2fastq.
"""

import sys
import argparse

def main(argv):

    parser = argparse.ArgumentParser(description='Run bcl2fastq')

    # Required arguments
    parser.add_argument('--input', required=True, help='Runfolder to demultiplex (required)',)
    parser.add_argument('--output', required=True, help='Output folder for bcl2fastq (required)',)

    # Optional arguments
    parser.add_argument('--barcode_missmatches',  help='Number of missmatches to allow (0, 1 or 2)',)
    parser.add_argument('--tiles',  help='Tiles to include.',)
    parser.add_argument('--use_base_mask',  help='Base mask to use.',)
    parser.add_argument('--additional_args',  help='Additional arguments to feed to bcl2fastq',)

    args = parser.parse_args()


    commandline = ["bcl2fastq",
         "--input-dir", args.input,
         "--output-dir", args.output]

    if args.barcode_missmatches:
        commandline.append("--barcode-mismatches " + args.barcode_missmatches)

    if args.tiles:
        commandline.append("--tiles " + args.tiles)

    if args.use_base_mask:
        commandline.append("--use_base_mask " + args.use_base_mask)

    if args.additional_args:
        commandline.append(args.additional_args)

    # TODO Actually run bcl2fastq!
    print " ".join(commandline)


if __name__ == "__main__":
    main(sys.argv[1:])
