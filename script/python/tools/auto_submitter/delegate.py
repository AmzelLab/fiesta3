"""Job Delegates implementation.

For each type of jobs, we have a delegate to handle that specific type.
The upper level submitter will only talks to these jobs delegate. Then
those delegates will maintain jobs through asking questions and making
decisions based on the answer they get.
"""

from abc import ABCMeta
from abc import abstractmethod

import logging

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class Decision(object):
    """Decision object can be executed by the manager (Submitter).

    This class essentially encapsulates a callback and its args.
    The higher level manager, who has more power, can call execute
    on every decision. Note that the decision can be executed only
    once.
    """

    def __init__(self, cb, *args):
        """Create a Decision object with a cb and its args"""
        self.__cb = cb
        self.__args = list(args) if args else None
        self.__executed = False

    def execute(self):
        """Execute this decision."""
        if self.__executed:
            return

        self.__executed = True
        if self.__args:
            return self.__cb(*self.__args)
        return self.__cb()


class JobDelegate(object):
    """
    An interface for all task delegates.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """Create a TaskDelegate with a task list."""
        self._jobs = {}
        self._job_stats = {}
        self._remote_channels = {}
        self._decisions = []

        self.__logger = logging.getLogger(
            "auto_submitter.delegate.JobDelegate")

    def add_job(self, job):
        """Add a job for this delegate to manage

        Args:
            job: job to add
        """
        if job["name"] in self._jobs:
            # Should be logged error.
            self.__logger.error("add_job: name duplicate [%s]", job["name"])
        else:
            self._jobs[job["name"]] = job
            self.__logger.info("add_job: %s", job["name"])

    @property
    def decisions(self):
        """get the internal decisions.

        Returns: List of decisions.
        """
        return self._decisions

    @abstractmethod
    def sync_remote(self):
        """Check the remote status through the provided channel."""
        pass


class GromacsJobDelegate(JobDelegate):
    """Job Delegate specifically serving Gromacs jobs."""

    def __init__(self):
        """Create a new job delegate for Gromacs"""
        super(GromacsJobDelegate, self).__init__()

        self.__logger = logging.getLogger(
            "auto_submitter.delegate.GromacsJobDelegate")

    def sync_remote(self):
        """Check the remote status through the provided channel.

        Sync the internal data with remote and make new decisions.
        """

        self.__logger.info("synced with remote.")
