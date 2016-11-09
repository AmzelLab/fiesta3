"""Some class functions on handling remote connections.

Remote class is a class that handles the status of the remote server.
"""
from abc import ABCMeta
from abc import abstractmethod

from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import STDOUT
from subprocess import TimeoutExpired

from datetime import datetime

import logging

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class Remote(object):
    """An interface to remote proxy object.
    """
    __metaclass__ = ABCMeta

    TIMEOUT = 60

    def __init__(self, server):
        """Creating a remote handler.

        Args:
            server: The remote server.
        """
        self.__logger = logging.getLogger('auto_submitter.remote.Remote')
        self._server = server

        if self._server == "":
            raise ValueError(
                "Remote object should have a non-empty server field.")

    def _run_command(self, command):
        """A protected function to run this remote command.

        Args:
            command: A string list, bash command run in remote

        Returns:
            A string contains the output of the remote command.
        """
        result = None
        try:
            result = check_output(
                command, timeout=Remote.TIMEOUT, stderr=STDOUT)
        except TimeoutExpired:
            command_string = " ".join(command)
            self.__logger.info("Remote command TIMEOUT: %s", command_string)
            return (False, "")
        except CalledProcessError as err:
            self.__logger.error("CalledProcessError: " +
                                err.output.decode("utf-8"))
            return (False, "")

        return (True, result.decode("utf-8").rstrip("\n"))

    @abstractmethod
    def _command_prefix(self, copy=False):
        """Get the command prefix to run remote commands (e.g. ssh)

        Args:
            copy: Boolean, is copying a file.

        Returns:
            List of string, command prefix.
        """
        pass

    @abstractmethod
    def job_status(self, user):
        """Query job status through ssh.

        Returns:
            A string list contains the job status returned by remote
        """
        pass

    def current_remote_time(self):
        """Returns the current time of remote (datetime object)"""
        self.__logger.info("Querying current time on remote.")
        command = self._command_prefix().extend([self._server, "date"])
        result = self._run_command(command)
        if result[0]:
            try:
                return datetime.strptime(result[1], "%a %b %d %H:%M:%S EST %Y")
            except ValueError:
                self.__logger.error("Failed to parse remote current time.")
                return datetime.min
        else:
            self.__logger.error("Failed to query current remote time")
            return datetime.min

    @abstractmethod
    def tail_log(self, job_id, working_folder, num_lines=1):
        """Returns the expect completion time of a job

        Args:
            job_id: The remote sbatch's job id.
            working_folder: The working folder for job_id
            n: number of lines of the tail.

        Returns:
            A string that contains the expect completion time of job_id.
        """
        pass

    @abstractmethod
    def copy_to_remote_and_submit(self, file_name, remote_folder):
        """Copy a batch script to remote and submit it.

        Args:
            file_name: File name

        Returns:
            The remote message.
        """
        pass

    @abstractmethod
    def cancel_job(self, job_id):
        """Cancel a job on remote.

        Args:
            job_id: the job id to cancel.
        """
        pass


class SlurmRemote(Remote):
    """A Remote Proxy that specifically configured for SLURM system.

    This class currently only supports SSH protocol to access Remote, which
    will be sufficient in most of the cases.
    """

    def __init__(self, server, shared=False):
        super(SlurmRemote, self).__init__(server)
        self.__logger = logging.getLogger("auto_submitter.remote.SlurmRemote")

        self.__shared = shared

    def _command_prefix(self, copy=False):
        """Get the command prefix to run remote commands (e.g. ssh)

        Args:
            copy: Boolean, is copying a file.

        Returns:
            List of string, command prefix.
        """
        prefix = "scp " if copy else "ssh "
        if self.__shared:
            prefix += "-o ControlMaster=no"
        if not copy:
            prefix += " " + self._server

        return prefix.split()

    def job_status(self, user):
        """Query job status through ssh.

        Returns:
            A string list contains the job status returned by remote
        """
        self.__logger.info("Querying job_status on remote.")
        status = self._run_command(self._command_prefix().extend(
            ["squeue", "-u", user]))

        if status[0]:
            job_status = status[1].split("\n")[1:]
            return [job.lstrip().split() for job in job_status]
        else:
            self.__logger.error("Failed to query job status.")
            return []

    def tail_log(self, job_id, working_folder, num_lines=1):
        """Returns the expect completion time of a job

        Args:
            job_id: The remote sbatch's job id.
            working_folder: The working folder for job_id

        Returns:
            A string that contains the expect completion time of job_id.
        """
        self.__logger.info("query log tail on remote.")
        command = self._command_prefix().extend(
            ["tail", str(num_lines),
             "%s/slurm-%s.out" % (working_folder, job_id)])
        result = self._run_command(command)

        if not result[0]:
            self.__logger.error("Failed to query ECT")
            return ""
        return result[1].rstrip().split("\n")

        # DELETE THE FOLLOWING AFTER COMPLETION
        # if len(re_list) == 0 or re_list[0] != "imb":
        #    self.__logger.info("remote job may not be ready when querying"
        #                       " expect_completion_time")
        #    return ""
        # else:
        #    return " ".join(re_list[-5:])

    def copy_to_remote_and_submit(self, file_name, remote_folder):
        """Copy a batch script to remote and submit it.

        Args:
            file_name: File name

        Returns:
            The remote message.
        """
        self.__logger.info("Copy and submit [%s] to remote.", file_name)

        cp_command = self._command_prefix(True).extend(
            [file_name, "%s:%s" % (self._server, remote_folder)])
        submit_command = self._command_prefix().extend(
            ["cd", remote_folder, "&&", "sbatch", file_name])

        if not self._run_command(cp_command)[0]:
            self.__logger.error("copy to remote failed [%s]", file_name)
            return ""

        submission = self._run_command(submit_command)
        if not submission[0]:
            self.__logger.error("submit to remote failed [%s]", file_name)
            return ""

        return submission[1]

    def cancel_job(self, job_id):
        """Cancel a job on remote.

        Args:
            job_id: the job id to cancel.
        """
        command = self._command_prefix().extend(["scancel", job_id])
        if not self._run_command(command)[0]:
            self.__logger.error("Cancelling job [%s] failed.", job_id)
