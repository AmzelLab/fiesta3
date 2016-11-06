"""Some class functions on handling remote connections.

Remote class is a class that handles the status of the remote server.
"""

from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import STDOUT
from subprocess import TimeoutExpired

import logging

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class Remote(object):
    """Handling remote status of jobs.
    """
    TIMEOUT = 60

    def __init__(self, server):
        """Creating a remote handler.

        Args:
            server: The remote server.
        """
        self.__server = server
        self.__logger = logging.getLogger('auto_submitter.remote.Remote')
        if self.__server == "":
            raise ValueError(
                "Remote object should have a non-empty server field.")

    def __run_command(self, command):
        """A private function to run this remote command.

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

    def job_status(self, user):
        """Query job status through ssh.

        Returns:
            A string list contains the job status returned by remote
        """
        self.__logger.info("Querying job_status on remote.")
        status = self.__run_command(
            ["ssh", "-o", "ControlMaster=no", self.__server,
             "squeue", "-u", user])

        if status[0]:
            job_status = status[1].split("\n")[1:]
            return [job.lstrip().split() for job in job_status]
        else:
            self.__logger.error("Failed to query job status.")
            return []

    def current_remote_time(self):
        """Returns the current time of remote"""
        self.__logger.info("Querying current time on remote.")
        result = self.__run_command(["ssh", "-o", "ControlMaster=no",
                                     self.__server, "date"])
        if result[0]:
            return result[1]
        else:
            self.__logger.error("Failed to query current remote time")
            return ""

    def expect_completion_time(self, job_id, working_folder):
        """Returns the expect completion time of a job

        Args:
            job_id: The remote sbatch's job id.
            working_folder: The working folder for job_id

        Returns:
            A string that contains the expect completion time of job_id.
        """
        self.__logger.info("Querying expect completion time on remote.")
        command_str = "ssh -o ControlMaster=no %s tail -1 %s/%s" % \
            (self.__server, working_folder, "slurm-%s.out" % job_id)
        result = self.__run_command(command_str.split())

        if not result[0]:
            self.__logger.error("Failed to query ECT")
            return ""

        re_list = result[1].split()
        if len(re_list) == 0 or re_list[0] != "imb":
            self.__logger.info("remote job may not be ready when querying"
                               " expect_completion_time")
            return ""
        else:
            return " ".join(re_list[7:])

    def copy_to_remote_and_submit(self, file_name, remote_folder):
        """Copy a batch script to remote and submit it.

        Args:
            file_name: File name

        Returns:
            The remote message.
        """
        self.__logger.info("Copy and submit [%s] to remote.", file_name)
        remote_cp = "scp -o ControlMaster=no %s %s:%s" % (
            file_name, self.__server, remote_folder)
        remote_submit = "ssh -o ControlMaster=no %s cd %s && sbatch %s" \
            % (self.__server, remote_folder, file_name)

        if not self.__run_command(remote_cp.split())[0]:
            self.__logger.error("copy to remote failed [%s]", file_name)
            return ""

        return self.__run_command(remote_submit.split())[1]

    def cancel_job(self, job_id):
        """Cancel a job on remote.

        Args:
            job_id: the job id to cancel.
        """
        remote_cancel = "ssh -o ControlMaster=no %s scancel %s" % (
                self.__server, job_id)
        if not self.__run_command(remote_cancel.split())[0]:
            self.__logger.error("Cancelling job [%s] failed.", job_id)
