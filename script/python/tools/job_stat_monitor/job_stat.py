#!/usr/bin/env /cm/shared/apps/python/3.4.2/bin/python3
# -*- coding: utf-8 -*-

"""Job status script running/testing on MARCC. (non-local script)
"""

from collections import namedtuple
from subprocess import check_output
from subprocess import STDOUT

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

_TIMEOUT = 10

# Convenient class JOB as namedtuple
Job = namedtuple('Job', ['name', 'partition', 'job_id', 'state', 'is_slow',
                         'nodelist', 'running_time', 'time_limit'])


def _run_bash(command_string):
    """TODO: Docstring for run_bash.
    Args:
        command_string: the bash command string

    Returns:
        Output of the bash command
    """
    result = None
    result = check_output(command_string, timeout=_TIMEOUT, stderr=STDOUT)
    return result.decode("utf-8").rstrip("\n")


def sqme():
    """list all my jobs.

    Returns:
        A dictionary contains primary info of jobs
    """
    job_list = []

    job_info = _run_bash("sqme").split("\n")[1:]
    for line in job_info:
        job_item = line.split(" ")
        job = Job(job_id=job_item[0],
                  partition=job_item[1],
                  name=job_item[2],
                  state=job_item[4],
                  running_time=job_item[5],
                  time_limit=job_item[6],
                  nodelist=job_item[8])
        job_list += job

    print job_list
    return job_list


def detail(jobs):
    """Fill out all information of current jobs.

    Args:
        jobs: a list of Job objects

    Returns:
        A dictionary contains detailed info of jobs
    """
    pass


def dump_json(jobs):
    """Dump job info to json string

    Args:
        jobs: a list of job objects after detailed.
    """
    pass


def main():
    """Main program to invoke job stats query.
    """
    dump_json(detail(sqme()))


if __name__ == "__main__":
    main()
