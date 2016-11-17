"""Implementation on the network gateway.

This module provides a common network gateway for all newtork
traffics. The purpose of the gateway is to help reduce network
traffics and distribute the information to the correct caller.
"""

import logging

from remote import RemoteFactory

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

    def __get_remote(self, remote_name):
        """Getter: from remote_name get the corresponding object.

        Args:
            remote_name: string, the name of the remote system.

        Returns:
            the remote object
        """
        try:
            return self.__remote[remote_name]
        except KeyError:
            self.__logger.error("No remote object named %s is requested.",
                                remote_name)
            return None

    def request_remote(self, remote_name, submission_system, shared_ssh=False):
        """Request a remote with its name and submission system.

        Args:
            remote_name: string, name of the remote machine
            submission_system: string, the remote's batch system.
            shared_ssh: boolean, whether to open up a shared ssh session.
        """
        create = False
        if remote_name in self.__remote:
            if self.__remote[remote_name].batch_system != submission_system:
                self.__logger.warning("use a new batch system on %s",
                                      remote_name)
                create = True
        else:
            create = True

        if create:
            self.__remote[remote_name] = RemoteFactory.create_remote(
                submission_system, remote_name, shared_ssh)
        return self.__remote[remote_name]

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
        return self.__get_remote(remote_name).copy_to_remote_and_submit(
            file_name, remote_folder)

    def cancel(self, remote_name, job_id):
        """Cancel a job with its job id.

        Args:
            remote_name: string, remote server
            job_id: string, job id
        """
        return self.__get_remote(remote_name).cancel_job(job_id)

    def run_on_remote(self, remote_name, command):
        """Run a remote command

        Args:
            remote_name: string, remote machine
            command: string, command to run on remote.

        Returns:
            string, the output of the command.
        """
        return self.__get_remote(remote_name).run_command(command)

    def tail_log(self, remote_name, job_id, working_folder, num_lines=1):
        """Returns the tail of a job's log

        Args:
            remote_name: the name of the remote server.
            job_id: The remote sbatch's job id.
            working_folder: The working folder for job_id
            n: number of lines of the tail.

        Returns:
            A string
        """
        return self.__get_remote(remote_name).tail_log(
            job_id, working_folder, num_lines)
