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
