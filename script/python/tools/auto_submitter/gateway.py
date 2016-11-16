"""Implementation on the network gateway.

This module provides a common network gateway for all newtork
traffics. The purpose of the gateway is to help reduce network
traffics and distribute the information to the correct caller.
"""

import logging

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class Singleton(type):
    """A decorator class for implementing singleton design pattern"""

    INSTANCE = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.INSTANCE:
            cls.INSTANCE[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.INSTANCE[cls]


class Gateway(object):
    """Network gateway impl."""

    __metaclass__ = Singleton

    def __init__(self):
        """Setup the singleton Gateway object"""
        self.__remote = {}
        self.__job_stats = {}
        self.__curr_time = None
        self.__logger = logging.getLogger("job_manager.gateway.Gateway")

    def __check_connection(self, remote_name):
        """check the connection for a specific remote machine

        Args:
            remote_name: string, remote machine

        Returns:
            Boolean
        """
        pass

    def job_stats(self, remote_name, job_name):
        """Query job stat for a specific job on remote

        Args:
            remote_name: string, the name of the remote machine
            job_name: string, the name of the job

        Returns:
            dict, job stat
        """
        pass

    def submit(self, remote_name, remote_folder, file_name):
        """Copy and submit a remote job

        Args:
            remote_name: string, remote server
            remote_folder: string, remote working folder
            file_name: string, the file to submit to remote

        Returns:
            string, job id
        """
        pass

    def cancel(self, remote_name, job_id):
        """Cancel a job with its job id.

        Args:
            remote_name: string, remote server
            job_id: string, job id
        """
        pass

    def run_on_remote(self, remote_name, command):
        """Run a remote command

        Args:
            remote_name: string, remote machine
            command: string, command to run on remote.

        Returns:
            string, the output of the command.
        """
        pass

