"""Job Specialists implementation.

For each type of jobs, we have a specialist to handle that specific type.
The job manager will only talks to these job specialists. Then
those specialists will maintain jobs.
"""

from abc import ABCMeta
from abc import abstractmethod

import logging

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class Specialist(object):
    """
    An interface for all job specialists.
    """
    __metaclass__ = ABCMeta

    def __init__(self, labor):
        """Create a specialist with a task list."""
        self._jobs = {}
        self._job_stats = {}
        self._labor = labor

        self.__logger = logging.getLogger(
            "job_manager.specialist.Specialist")

    @abstractmethod
    def _check_job_metadata(self, job):
        """Check job's metadata

        Args:
            job: dict type, job item.

        Returns:
            Boolean
        """
        pass

    def _check_duplicated_name(self, name):
        """Check whether name is exists

        Args:
            name: string, job name

        Returns:
            Boolean
        """
        if name in self._jobs:
            self.__logger.error("name duplicate [%s]", name)
            return False

        return True

    @property
    def jobs(self):
        """Jobs getter"""
        return self._jobs.values()

    @property
    def job_stats(self):
        """Job stats getter"""
        return self._job_stats.values()

    @abstractmethod
    def __add_job_handler(self, job):
        """add job will call this handler to generate initial status
        on this job.

        Args:
            job: dict of job item.
        """
        pass

    def add_job(self, job):
        """Add a job for this delegate to manage

        Args:
            job: job to add
        """
        # Validating inputs
        if not (self._check_job_metadata(job) and
                self._check_duplicated_name(job["name"])):
            return False

        self._jobs[job["name"]] = job
        self.__logger.info("add_job: %s", job["name"])
        self.__add_job_handler(job)
        return True

    @abstractmethod
    def sync_remote(self):
        """Check the remote status through the provided channel."""
        pass


class GromacsSpecialist(Specialist):
    """Job Delegate specifically serving Gromacs jobs."""

    REQUIRED = ["nameBase", "sectionNum", "mdp", "continuation"]

    def __init__(self, labor):
        """Create a new job delegate for Gromacs"""
        super(GromacsSpecialist, self).__init__(labor)

        self.__logger = logging.getLogger(
            "job_manager.specialist.GromacsSpecialist")

    def _check_job_metadata(self, job):
        """Check job's metadata

        Args:
            job: dict type, job item.

        Returns:
            Boolean
        """
        for key in GromacsSpecialist.REQUIRED:
            if key not in job:
                self.__logger.error(
                    "invalid gromacs job: no required field [%s]", key)
                return False

        return True

    def __add_job_handler(self, job):
        """Add job handler for gromacs job.

        Args:
            job: dict of job item.
        """
        pass

    def __status_update_handler(self, response):
        pass

    def __submitted_handler(self, response):
        pass

    def sync_remote(self):
        """Check the remote status through the provided channel.

        Sync the internal data with remote and make new decisions.
        """

        self.__logger.info("synced with remote.")


class TestSpecialist(Specialist):
    """Job Specialist specifically serving tests."""

    def __init__(self, labor):
        """Create a new job delegate for Gromacs"""
        super(TestSpecialist, self).__init__(labor)

        self.__logger = logging.getLogger(
            "job_manager.specialist.TestSpecialist")

    def _check_job_metadata(self, job):
        """Check job's metadata in test

        Args:
            job: dict type, job item.

        Returns:
            Boolean
        """
        return True

    def __add_job_handler(self, job):
        """Add job handler for gromacs job.

        Args:
            job: dict of job item.
        """
        pass


class SpecialistFactory(object):
    """Specialist factory implementation.

    From here you can create all kinds of specialist by the provided
    common object creation method.
    """
    LOGGER = logging.getLogger("job_manager.specialist.SpecialistFactory")

    # Only needs to append this dict to add new Specialist.
    SPECIALIST_TYPE = {
        "Gromacs": GromacsSpecialist,
        "Test": TestSpecialist
    }

    @staticmethod
    def create_specialist_with_labor(ftype, labor):
        """call this method to create a specialist of certain ftype

        Args:
            ftype: string, factory type

        Returns:
            A specialist instance.
        """
        if ftype not in SpecialistFactory.SPECIALIST_TYPE:
            SpecialistFactory.LOGGER.error(
                "no specialist named [%s] is available.",
                ftype + "Specialist")
            return None

        SpecialistFactory.LOGGER.info("create a specialist of type [%s]",
                                      ftype)
        return SpecialistFactory.SPECIALIST_TYPE[ftype](labor)
