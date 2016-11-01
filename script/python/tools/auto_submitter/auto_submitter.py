#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A program that serves as a manager for automatically submitting
a bunch of batch jobs.

Jobs parameters are packaged into a json file as input. The manager can
read the parameters in two mode: start mode and reset mode.

Usage: Please run ./auto_submitter.py -h
"""

from json import load
import argparse
import logging
from time import strftime

from submitter import AutoSubmitter
from submitter import TestSubmitter

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

DESCRIPTION = "Batch Job Manager (Auto Submitter)"

LOGGER = logging.getLogger('auto_submitter')
LOGGER.setLevel(logging.DEBUG)

LOG_FILE = 'auto_submitter_%s.log' % strftime('%X_%d_%b_%Y')
FILE_HANDLER = logging.FileHandler(LOG_FILE)
FILE_HANDLER.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter(
    "[%(levelname)s %(asctime)s %(name)s] %(message)s")
FILE_HANDLER.setFormatter(FORMATTER)

LOGGER.addHandler(FILE_HANDLER)


def main():
    """Main entry to the program.

    Parse the command line args and turn it in to the submitter object.
    """
    LOGGER.info("auto_submitter starts")

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--json', type=argparse.FileType('r'), nargs='?',
                        default='jobs.json',
                        help="A json file encoding all jobs' info")
    parser.add_argument('--remote', type=str, nargs='?', default='marcc',
                        action='store', help="The remote computing center.")
    parser.add_argument('--test', default=False, action='store_true',
                        help="Run this program in test mode")
    args = parser.parse_args()

    jobs_data = None
    try:
        jobs_data = load(args.json)
    finally:
        args.json.close()

    submitter = TestSubmitter(jobs_data, args.remote) if args.test else \
        AutoSubmitter(jobs_data, args.remote)
    LOGGER.info("starting %s with remote: %s",
                submitter.__class__.__name__, args.remote)
    submitter.run()


if __name__ == "__main__":
    main()
