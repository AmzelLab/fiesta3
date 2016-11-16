"""Implementation of Job Manager

The job manager distributes jobs to job specialists. It hires all labor
resources for all job specialists. The manager collects reports from
all specialists as well.
"""

import logging
from json import dump
from concurrent.futures import ThreadPoolExecutor

from specialist import SpecialistFactory

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
        if callback is None:
            self.__executor.submit(request.action(), *request.args())
        else:
            self.__executor.submit(request.action(),
                                   *request.args()).add_done_callback(callback)


class JobManager(object):
    """Job manager implementation:

    Allocate resources for workers and assign jobs to specialists
    (delegates).
    """
    HEADER_FIELDS = ["title", "data"]
    REQUIRED = ["name", "type", "remote", "batchType", "userId",
                "directory", "timeLimit", "numOfNodes", "numOfProcs",
                "numOfThrs", "partition"]

    def __init__(self):
        super(JobManager, self).__init__()
        self.__specialists = {}
        self.__labors = None

        self.__logger = logging.getLogger("job_manager.manager.JobManager")

    def __check_job_header(self, job):
        """Check whether the job header is valid.

        Args:
            job: dict, job configuration

        Returns: Boolean
        """
        for key in JobManager.HEADER_FIELDS:
            if key not in job:
                self.__logger.error("invalid type: no field [%s] in header",
                                     key)
                return False

        return True

    def __check_job_meta_data(self, item):
        """Check whether the job is valid by its meta data.

        Args:
            item: dict, job item

        Returns: boolean, is valid.
        """
        for key in JobManager.REQUIRED:
            if key not in item:
                self.__logger.error("invalid job: no required field [%s]",
                                     key)
                return False

        return True

    def __add_job(self, job):
        """Add a single job for the manager to manage.
        The manager will assign the job to a specialist
        and tell specialists to use the labor the manager
        hired. The manager will also order a connection
        for that job in the network.

        Args:
            job: dict, job to manage
        """
        if not self.__check_job_meta_data(job):
            self.__logger.error("invalid job meta data")
            return False

        job_type = job["type"]
        if job_type not in self.__specialists:
            self.__specialists[job_type] = \
                SpecialistFactory.create_specialist_with_labor(
                    job_type, self.__labors)
            if not self.__specialists[job_type]:
                return False

        specialist = self.__specialists[job_type]
        if not specialist.add_job(job):
            self.__logger.info("job [%s] declined", job["name"])
            return False

        self.__logger.info("job [%s] added", job["name"])
        return True

    def __remove_job(self, job):
        """Remove a job that is currently managed.

        Args:
            job: job to remove
        """
        pass

    @staticmethod
    def __header_invalid_string():
        """Generate a result string when invalid headers are added.

        Returns:
            a result string returned back to client
        """
        return "Your jobs are rejected due to invalid header.\n"\
               "Job header should contain the following required fields:\n\t"\
               "\t %s\n" % "\t".join(JobManager.HEADER_FIELDS)

    @staticmethod
    def __add_jobs_result(accepted, declined):
        """Generate a result string when adding jobs are succeeded or
        partially succeeded.

        Args:
            accepted: list of string, accepted jobs' name
            declined: list of string, declined jobs' name
        Returns:
            a result string returned back to client
        """
        return "ACCEPTED: %s\nDECLINED: %s\n" % \
                (" ".join(accepted), " ".join(declined))

    def add_jobs(self, jobs):
        """add jobs for the manager to manage.
        A convenient wrapper for add_job(job).

        Args:
            jobs: list of dict, jobs to manage
        """
        if not self.__check_job_header(jobs):
            self.__logger.error("invalid header type. rejected.")
            return JobManager.__header_invalid_string()

        accepted = []
        declined = []
        for job in jobs["data"]:
            if self.__add_job(job):
                accepted.append(job["name"])
            else:
                declined.append(job["name"])

        return self.__add_jobs_result(accepted, declined)

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
        snap_data = {"title": "Snapshot", "data": []}
        for specialist in self.__specialists.values():
            snap_data["data"].extend(specialist.jobs())

        with open(filename, "w") as snapshot:
            dump(snap_data, snapshot, indent=4, sort_keys=True)

        return "snapshot dumped to file %s" % filename

    def take_office(self):
        """Start to manage jobs. Hiring labors and Waiting
        for jobs"""
        self.__labors = Labor()
