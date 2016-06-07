#!/usr/bin/python

"""
Usage: check_summary_report_modtime.py </path/with/runfolders> <summary report time age in seconds>

This script will search a the give root directory for runfolder and return a json array of all runfolders
which which have a summary report file that is older than the given time in seconds.

"""

import argparse
import os
import json
import sys
import time
import logging

# create logger
logger = logging.getLogger('check_summary_report_modtime')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

def check_file_older_than(file_to_check, threshold):
    summary_report_mtime = os.path.getmtime(file_to_check)
    logger.debug("summary report mtime: {0}".format(summary_report_mtime))

    current_time = time.time()
    logger.debug("current time: {0}".format(current_time))

    is_old_enough = (current_time - summary_report_mtime) > threshold
    logger.debug("is old enough: {0}".format(is_old_enough))

    return is_old_enough

def get_old_enough_runfolders(path_to_search, minimum_summary_report_age, runfolders):
    for runfolder in runfolders:
        logger.debug("runfolder: {0}".format(runfolder))
        summary_report = os.path.join(path_to_search, runfolder, "Summary", "summaryReport.html")
        if os.path.isfile(summary_report) and check_file_older_than(summary_report, minimum_summary_report_age):
            logger.info("runfolder: {0} is old enough.".format(runfolder))
            yield runfolder
        else:
            logger.info("runfolder: {0} is not old enough or summary report does not exist.".format(runfolder))


def main():

    parser = argparse.ArgumentParser(description='Filter runfolders in a directory based on summary report '
                                                 'modtime.')

    # Required arguments
    parser.add_argument('--directory', required=True, help='Root directory to search for runfolders in.')
    parser.add_argument('--modtime', required=True, help='The summary file needs to be older than this')
    parser.add_argument('--debug', required=False, action='store_true', help='Set to debug mode, possible value 0 or 1.')
    parser.set_defaults(debug=False)
    try:
        args = parser.parse_args()
    except Exception as e:
        print sys.argv[0]

    path_to_search = args.directory
    minimum_summary_report_age = int(args.modtime)

    # set log level
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.debug("minimum file age: {0}".format(minimum_summary_report_age))
    runfolder_list = [name for name in os.listdir(path_to_search) if os.path.isdir(os.path.join(path_to_search, name))]
    old_enough_runfolders = list(get_old_enough_runfolders(path_to_search, minimum_summary_report_age, runfolder_list))
    print(json.dumps(old_enough_runfolders))

if __name__ == "__main__":
    main()
