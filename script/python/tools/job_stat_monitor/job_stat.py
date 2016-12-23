#!/usr/bin/env /cm/shared/apps/python/3.4.2/bin/python3
# -*- coding: utf-8 -*-

"""Job status script running/testing on MARCC. (non-local script)
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta
from subprocess import check_output
from subprocess import STDOUT

from json import dump

import asyncio
import re
import sys

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

_TIMEOUT = 10


def _run_bash(command_string):
    """Simply run a bash command.
    Args:
        command_string: the bash command string

    Returns:
        Output of the bash command
    """
    result = None
    result = check_output(command_string, shell=True,
                          timeout=_TIMEOUT, stderr=STDOUT)
    return result.decode("utf-8").rstrip("\n")


def _fetch_first_node(nodelist_string):
    """fetch the first node in the nodelist as a rep.
    The nodelist may have forms:
        1) compute0530
        2) compute[0488,0493,0582,0663]
        3) compute[0396-0397,0414-0416,0664-0666]
    Args:
        nodelist_string: the node list string returned by SLURM.

    Returns:
        the first node in the list
    """
    if not nodelist_string:
        raise ValueError("Nodelist string shouldn't be empty")

    matcher = re.compile('([0-9]+|[a-z]+)')
    matched = matcher.findall(nodelist_string)
    return matched[0] + matched[1]


def _job_detail(job):
    """Extend details for a job item.

    Args:
        job: job object. (namedtuple defined as above)
    """
    # This is only for jobs that are running
    if job["state"] != "RUNNING":
        return job

    # First we want to run "scontrol show jobid" on every job.
    scontrol = "scontrol show jobid %s | grep StdOut" % job["job_id"]
    output = _run_bash(scontrol)
    log_path = output.strip().split('=')[1]

    # Second we want to fetch out the last 10 lines of the log
    job["log"] = _run_bash("tail %s" % log_path)

    # if we are on gpu, we should always check whether our jobs
    # are running slow
    if job["partition"] != "gpu":
        return job

    # check is_slow on gpu jobs using perf
    # we need to determine a representative process of that job
    # always pick the last one in the node list for measurement
    node = _fetch_first_node(job["nodelist"])
    list_pid = "ssh %s ps -C gmx_mpi -o pid" % node
    output = _run_bash(list_pid)
    pid = output.split("\n").pop()

    # Check CPU freq using perf
    check_cpu_freq = "ssh %s perf stat -p %s -o tmp.%s.cpu sleep 0.2" % (
        node, pid, node)
    _run_bash(check_cpu_freq)
    output = _run_bash("grep GHz ~/tmp.%s.cpu" % node).split()

    # Magic number:
    # Output should look like:
    # ['7,381,669,365', 'cycles', '#', '2.486', 'GHz', '[100.00%]']
    job["is_slow"] = False if float(output[3]) > 2.0 else True

    # Clean up and return
    _run_bash("rm ~/tmp.%s.cpu" % node)
    return job


def source():
    """source all my recent jobs. (recent 3 days)

    Returns:
        A dictionary contains primary info of jobs
    """
    job_list = []

    job_info = _run_bash("sqme").split("\n")[2:]
    # Another source:
    sacct = "sacct --format=jobid,partition,jobname,"       \
            "user,state,elapsed,timelimit,nnodes,nodelist " \
            "--state=completed,cancelled,failed,timeout"

    # Add starttime flag.
    week_ago = datetime.today() - timedelta(days=3)
    sacct += " --starttime=%s" % week_ago.strftime("%m/%d/%y")

    # Combine source
    job_info.extend(_run_bash(sacct).split("\n")[2:])

    for line in job_info:
        job_item = line.split()

        # Here we omit some invalid job lines.
        # See the above format of query output, length=9
        # And each column's fieldname is labelled above.
        if len(job_item) < 9:
            continue

        job = dict(job_id=job_item[0],
                   partition=job_item[1],
                   name=job_item[2],
                   state=job_item[4],
                   is_slow=False,
                   running_time=job_item[5],
                   time_limit=job_item[6],
                   nodelist=job_item[8],
                   log="N/A")
        job_list.append(job)

    return job_list


def detail(jobs, executor):
    """Fill out all information of current jobs.

    Args:
        jobs: a list of Job objects

    Returns:
        A dictionary contains detailed info of jobs
    """
    if not jobs:
        return []

    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, _job_detail, job) for job in jobs]
    loop.run_until_complete(asyncio.wait(tasks))
    return [task.result() for task in tasks]


def dump_json(jobs):
    """Dump job info to json string

    Args:
        jobs: a list of job objects after detailed.
    """
    json_dict = {"time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    json_dict["jobs"] = jobs
    dump(json_dict, sys.stdout)


def main():
    """Main program to invoke job stats query.
    """
    executor = ThreadPoolExecutor(max_workers=8)
    dump_json(detail(source(), executor))
    executor.shutdown()


if __name__ == "__main__":
    main()
