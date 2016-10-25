"""Classes implements submitter in different modes.
"""

from abc import ABCMeta
from abc import abstractmethod

from json import dump
from json import load

import logging

from batch import GromacsBatchFile
from remote import Remote

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


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
    def run(self):
        """Run this submitter
        """
        pass


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

    def run(self):
        """Test run for submitter
        """
        self.__logger.info("TestSubmitter engine starts.")
        self.__logger.info("managing %s", self._data["context"])
        self.__logger.info("User: %s", self._data["userId"])

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
            "auto_submitter.submitter.TestSubmitter")

    def run(self):
        """Run the scheduler to manage all jobs.
        """
        pass
