"""Classes implements submitter in different modes.
"""

from abc import ABCMeta
from abc import abstractmethod

from json import dump
from json import load

from concurrent.futures import ThreadPoolExecutor

import logging

from batch import GromacsBatchFile
from remote import Remote

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

# Define some constants
JOB_ID = 1
JOB_NAME = 2
JOB_STAT = 4


class SubmitterBase(object):
    """Jobs submitter implementation.

    This submitter automatically detect jobs' status, generates new batch
    files and submits files to the remote server. In current design, a single
    Submitter can only work with a single remote computing center.
    """
    __metaclass__ = ABCMeta

    def __init__(self, jobs_data, remote):
        """Create the submitter object

        Args:
            jobs_data: dict type, all information of the jobs to be managed
            remote: string type, the remote machine
        """
        super(SubmitterBase, self).__init__()
        self._data = jobs_data
        self._remote = Remote(remote)

    @abstractmethod
    def _log_start(self):
        """logging when engine starts"""
        pass

    @abstractmethod
    def run(self):
        """Run this submitter
        """
        self._log_start()


class TestSubmitter(SubmitterBase):
    """A simple submitter works in the test mode."""

    def __init__(self, jobs_data, remote):
        """Create a test submitter object

        Args:
            jobs_data: dict type, all information of the jobs to be managed
            remote: string type, the remote machine
        """
        super(TestSubmitter, self).__init__(jobs_data, remote)
        self.__logger = logging.getLogger(
            "auto_submitter.submitter.TestSubmitter")

    def _log_start(self):
        """logging when TestSubmitter engine starts"""
        self.__logger.info("%s engine starts.", self.__class__.__name__)
        self.__logger.info("managing %s", self._data["context"])
        self.__logger.info("User: %s", self._data["userId"])

    def run(self):
        """Test run for submitter
        """
        super(TestSubmitter, self).run()

        # Accessing remote
        remote_time = self._remote.current_remote_time()
        if remote_time != "":
            self.__logger.info("Accessing remote success")
            self.__logger.info("Remote time: %s", remote_time)
        else:
            self.__logger.error("Accessing remote failed.")

        # Generating Batch file
        self.__logger.info("Reading data title: %s",
                           self._data["data"]["title"])
        items = self._data["data"]["items"]
        for job_item in items:
            if job_item["kind"] == "Gromacs":
                batch_file = GromacsBatchFile(job_item, job_item["name"])
                batch_file.file()

        self.__logger.info("Test completed.")


class AutoSubmitter(SubmitterBase):
    """Auto Submitter implementation"""

    def __init__(self, jobs_data, remote):
        """Create an auto submitter object

        Args:
            jobs_data: dict type, all information of the jobs to be managed
            remote: string type, the remote machine
        """
        super(AutoSubmitter, self).__init__(jobs_data, remote)
        self.__logger = logging.getLogger(
            "auto_submitter.submitter.AutoSubmitter")
        self.__executor = ThreadPoolExecutor(max_workers=4)
        self.__job_table = self._data["data"]["items"]
        self.__ids = {}

    def __checkin_items(self):
        """check the formats of input job tables"""
        index = 0
        for item in self.__job_table:
            if len(item["name"]) > 8:
                self.__logger.critical("job name has a length > 8")
                return False
            self.__logger.info("put job %s in job table", item["name"])

            if item["name"] in self.__ids:
                self.__logger.critical("duplicate job name %s", item["name"])
                return False

            item["name"] = index
            item["jobId"] = ""
            item["expCompletion"] = 0
            index += 1

        return True

    def __time_to_completion(self, job_id, work_dir):
        """Get the time to completion for specific job_id

        Args:
            job_id: The remote sbatch's job id.
            working_folder: The working folder for job_id

        Returns:
            An int, time to completion in seconds.
        """
        remote_current = self._remote.current_remote_time()
        expt_completion = self._remote.expect_completion_time(job_id, work_dir)
        print(remote_current)
        print(expt_completion)

    def __get_job_stats(self):
        """put remote job status onto the internal data structure"""
        job_stats = self._remote.job_status()

        for job in job_stats:
            item = self.__job_table[self.__ids[job[JOB_NAME]]]
            item["jobId"] = job[JOB_ID]
            item["expCompletion"] = self.__time_to_completion(
                job[JOB_ID], item["directory"])

    def __initialize(self):
        """Initialize the internal job table.

        Returns:
            Boolean, is initialized.
        """
        self.__logger.info("initializing...")
        self.__logger.info("reading remote job status")

        if not self.__checkin_items():
            return False

        self.__get_job_stats()

        return True

    def _log_start(self):
        """logging when AutoSubmitter engine starts"""
        self.__logger.info("%s engine starts.", self.__class__.__name__)
        self.__logger.info("managing %s", self._data["context"])
        self.__logger.info("User: %s", self._data["userId"])

    def run(self):
        """Run the scheduler to manage all jobs.
        """
        super(AutoSubmitter, self).run()

        # Initiate jobs
        if not self.__initialize():
            return
