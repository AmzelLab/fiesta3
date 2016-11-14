"""Implementation of Job Manager

The job manager distributes jobs to job specialists. It hires all labor
resources for all job specialists. The manager collects reports from
all specialists as well.
"""

from concurrent.futures import ThreadPoolExecutor
from queue import Queue

__author__ = "davislong198833@gmail.com (Yunlong Liu)"

NUM_THREADS = 8


class Labor(object):
    """Labor class. Do all real work"""

    def __init__(self, num_workers=NUM_THREADS):
        super(Labor, self).__init__()
        self.__executor = ThreadPoolExecutor(max_workers=num_workers)

    def perform(self, request, callback):
        """do what the request said faithfully.

        When the request is completed, run the handler callback.

        Args:
            request: the task request.
            callback: run the callback after task is completed.
        """
        self.__executor.submit(request.action(),
                               request.args()).add_done_callback(callback)


class JobManager(object):
    """Job manager implementation:

    Allocate resources for workers and assign jobs to specialists
    (delegates).
    """

    def __init__(self):
        super(JobManager, self).__init__()
        self.__specialists = None
        self.__labors = None

    def add_job(self, job):
        """Add a single job for the manager to manage.
        The manager will assign the job to a specialist
        and tell specialists to use the labor the manager
        hired. The manager will also order a connection
        for that job in the network.

        Args:
            job: dict, job to manage
        """
        pass

    def add_jobs(self, jobs):
        """add jobs for the manager to manage.
        A convenient wrapper for add_job(job).

        Args:
            jobs: list of dict, jobs to manage
        """
        for job in jobs:
            self.add_job(job)

    def remove_jobs(self, jobs):
        """drop some jobs

        Args:
            jobs: jobs to drop
        """
        pass

    def snapshot(self, filename):
        """take the current snapshot of all jobs status.
        Write a job status to a json file, named as filename

        Args:
            filename: json filename
        """
        pass

    def take_office(self):
        """Start to manage jobs. Hiring labors and Waiting
        for jobs"""
        self.__labors = Labor()
