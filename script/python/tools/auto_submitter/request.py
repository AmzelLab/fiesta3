"""Declaration and implementation on Request object.
"""

from abc import ABCMeta
from abc import abstractmethod

from gateway import Gateway

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class Request(object, metaclass=ABCMeta):
    """An interface for request object."""

    def __init__(self):
        """Create a request instance"""
        pass

    @abstractmethod
    def action(self):
        """The action that the request would perform"""
        pass

    def args(self):
        """The args for the action"""
        return ()


class GeneralRequest(Request):
    """General request"""

    def __init__(self, act=None, *args):
        """Create a request instance"""
        super(GeneralRequest, self).__init__()
        self.__act = act
        self.__args = list(args)

    def action(self):
        """The action that the request would perform"""
        return self.__act

    def args(self):
        """The args for the action"""
        return iter(self.__args)


class NetworkRequest(Request):
    """A request that goes through network, All network
    request objects has a gateway object available internally.
    """

    def __init__(self, remote_name):
        super(NetworkRequest, self).__init__()
        self._args = [remote_name]
        self._gateway = Gateway()

    def action(self):
        """action for Network"""
        pass

    def args(self):
        """The args for the action"""
        for arg in self._args:
            yield arg


class JobStatsRequest(NetworkRequest):
    """A convenient wrapper class for querying job status"""

    def __init__(self, remote_name, username, job_name):
        super(JobStatsRequest, self).__init__(remote_name)
        self._args.extend([username, job_name])

    def action(self):
        """action for querying job stats"""
        return self._gateway.job_stats


class CopyAndSubmitRequest(NetworkRequest):
    """A convenient wrapper class for copying and submitting file"""

    def __init__(self, remote_name, remote_folder, file_name):
        super(CopyAndSubmitRequest, self).__init__(remote_name)
        self._args.extend([remote_folder, file_name])

    def action(self):
        """action for querying job stats"""
        return self._gateway.submit


class CancelJobRequest(NetworkRequest):
    """A convenient wrapper class for copying and submitting file"""

    def __init__(self, remote_name, job_id):
        super(CancelJobRequest, self).__init__(remote_name)
        self._args.append(job_id)

    def action(self):
        """action for querying job stats"""
        return self._gateway.cancel


class LogRequest(NetworkRequest):
    """A convenient wrapper class for the latest job logs"""

    def __init__(self, remote_name, job_id, working_dir, num_lines=1):
        super(LogRequest, self).__init__(remote_name)
        self._args.extend([job_id, working_dir, num_lines])

    def action(self):
        """action for querying job stats"""
        return self._gateway.tail_log


class RemoteCommandRequest(NetworkRequest):
    """A convenient wrapper class for executing remote commands"""

    def __init__(self, remote_name, action_str):
        super(RemoteCommandRequest, self).__init__(remote_name)
        self._args.append(action_str)

    def action(self):
        """action for querying job stats"""
        return self._gateway.run_on_remote


class RequestRemoteRequest(NetworkRequest):
    """A convenient wrapper class for request remote servers"""

    def __init__(self, remote_name, batch_type):
        super(RequestRemoteRequest, self).__init__(remote_name)
        self._args.append(batch_type)

    def action(self):
        """action for querying job stats"""
        return self._gateway.request_remote


class ResetNetworkRequest(Request):
    """A convenient wrapper class for resetting the network gateway"""

    def __init__(self):
        super(ResetNetworkRequest, self).__init__()

    def action(self):
        """action for querying job stats"""
        return Gateway().reset
