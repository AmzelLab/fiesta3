"""Declaration and implementation on Request object.
"""

from abc import ABCMeta
from abc import abstractmethod

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class Request(object):
    """An interface for request object."""
    __metaclass__ = ABCMeta

    def __init__(self):
        """Create a request instance"""
        pass

    @abstractmethod
    def action(self):
        """The action that the request would perform"""
        pass

    @abstractmethod
    def args(self):
        """The args for the action"""
        pass


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
    """A request that goes through network"""

    def __init__(self, arg):
        super(NetworkRequest, self).__init__()
        self.arg = arg

    def action(self):
        """action for Network"""
        pass

    def args(self):
        """args for network action"""
        pass


class JobStatsRequest(NetworkRequest):
    """A convenient wrapper class for querying job status"""

    def __init__(self, arg):
        super(JobStatsRequest, self).__init__()
        self.arg = arg

    def action(self):
        """action for querying job stats"""
        pass

    def args(self):
        """args for querrying job stats"""
        pass


class CopyAndSubmitRequest(NetworkRequest):
    """A convenient wrapper class for copying and submitting file"""

    def __init__(self, arg):
        super(CopyAndSubmitRequest, self).__init__()
        self.arg = arg

    def action(self):
        """action for querying job stats"""
        pass

    def args(self):
        """args for querrying job stats"""
        pass


class CancelJobRequest(NetworkRequest):
    """A convenient wrapper class for copying and submitting file"""

    def __init__(self, arg):
        super(CancelJobRequest, self).__init__()
        self.arg = arg

    def action(self):
        """action for querying job stats"""
        pass

    def args(self):
        """args for querrying job stats"""
        pass
