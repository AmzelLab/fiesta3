"""Some class functions on handling remote connections.

Remote class is a class that handles the status of the remote server.
"""
from abc import ABCMeta
from abc import abstractmethod

from collections import namedtuple

from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import STDOUT
from subprocess import TimeoutExpired

from datetime import datetime

import logging

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

JobStat = namedtuple('JobStat', ['name', 'id', 'machine', 'stat', 'note'])


class Remote(object, metaclass=ABCMeta):
    """An interface to remote proxy object.
    """

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

    @property
    def remote(self):
        """return the remote name

        Returns:
            string, the name of the remote
        """
        return self._server

    @property
    @abstractmethod
    def batch_system(self):
        """return the name of the batch system

        Returns:
            string, the name of the batch system
        """
        return ""

    @abstractmethod
    def _command_prefix(self, copy=False):
        """Get the command prefix to run remote commands (e.g. ssh)

        Args:
            copy: Boolean, is copying a file.

        Returns:
            List of string, command prefix.
        """
        pass

    def run_command(self, command):
        """Run a user provided command.

        Args:
            command: string, just like a local command.

        Returns:
            output
        """
        return self._run_command(self._command_prefix().extend(command.split()))

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
        """Returns the tail of a job's log

        Args:
            job_id: The remote sbatch's job id.
            working_folder: The working folder for job_id
            n: number of lines of the tail.

        Returns:
            A string
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
    JOB_ID = 0
    JOB_NAME = 2
    JOB_STAT = 4
    JOB_MACHINE = 7

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

    @property
    def batch_system(self):
        """return the name of the batch system

        Returns:
            string, the name of the batch system
        """
        return "slurm"

    def job_status(self, user):
        """Query job status through ssh.

        Returns:
            A list of JobStat.
        """
        self.__logger.info("Querying job_status on remote.")
        status = self._run_command(self._command_prefix().extend(
            ["squeue", "-u", user]))

        if status[0]:
            job_status = status[1].split("\n")[1:]

            # return list: job_stats
            job_stats = []
            for job in job_status:
                raw_stat = job.lstrip().split()
                job_stats.append(
                    JobStat(name=raw_stat[SlurmRemote.JOB_NAME],
                            id=raw_stat[SlurmRemote.JOB_ID],
                            stat=raw_stat[SlurmRemote.JOB_STAT],
                            note="",
                            machine=raw_stat[SlurmRemote.JOB_MACHINE]))

            return job_stats
        else:
            self.__logger.error("Failed to query job status.")
            return []

    def tail_log(self, job_id, working_folder, num_lines=1):
        """Returns the tail of a job's log

        Args:
            job_id: The remote sbatch's job id.
            working_folder: The working folder for job_id
            n: number of lines of the tail.

        Returns:
            A string
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


class RemoteFactory(object):
    """Specialist factory implementation.

    From here you can create all kinds of specialist by the provided
    common object creation method.
    """
    LOGGER = logging.getLogger("job_manager.remote.RemoteFactory")

    # Only needs to append this dict to add new Specialist.
    REMOTE_TYPE = {
        "slurm": SlurmRemote,
    }

    @staticmethod
    def create_remote(stype, remote_name, shared=False):
        """call this method to create a remote object of certain type

        Args:
            stype: string, the type of the submission system

        Returns:
            A remote instance.
        """
        if stype not in RemoteFactory.REMOTE_TYPE:
            RemoteFactory.LOGGER.error(
                "no remote named [%s] is available.",
                stype + "Remote")
            return None

        RemoteFactory.LOGGER.info("create a remote of type [%s]",
                                  stype)
        return RemoteFactory.REMOTE_TYPE[stype](remote_name, shared)
