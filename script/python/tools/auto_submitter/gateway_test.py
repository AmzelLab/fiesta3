"""unit test for gateway.py
"""

import unittest
from unittest import mock

from remote import Remote
from remote import SlurmRemote
from gateway import Gateway

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class TestGateway(unittest.TestCase):
    """Test cases for Gateway"""

    def setUp(self):
        """Setups for unittests"""
        self.__gateway = Gateway()

    def test_singleton(self):
        """Testing Gateway object is a singleton."""
        gateway_a = Gateway()
        gateway_b = Gateway()
        self.assertTrue(gateway_a == gateway_b)

    def test_direct_actions_with_unregistered(self):
        """Testing Gateway functionality with direct actions only.
        By saying direct actions, we mean actions with no cache."""
        self.__gateway.reset()
        output = self.__gateway.submit("RANDOM", "RANDOM", "RANDOM")
        self.assertTrue(output == None)

    def test_direct_actions_with_registered(self):
        """Testing Gateway functionality with direct actions only.
        By saying direct actions, we mean actions with no cache."""
        self.__gateway.reset()
        output = self.__gateway.submit("RANDOM", "RANDOM", "RANDOM")
        self.assertTrue(output == None)

    @mock.patch("remote.Remote.run_command", return_value=(False, ""))
    def test_request_remote_not_connected(self, test_remote):
        self.__gateway.reset()
        self.assertFalse(self.__gateway.request_remote("RANDOM", "slurm"))

    def test_request_remote_no_such_remote(self):
        self.__gateway.reset()
        self.assertFalse(self.__gateway.request_remote("Random", "Slurm"))

    @mock.patch("remote.Remote.run_command", return_value=(True, ""))
    def test_request_remote_normal(self, test_remote):
        self.__gateway.reset()
        self.assertTrue(self.__gateway.request_remote("RANDOM", "slurm"))

    @mock.patch("remote.Remote.run_command", return_value=(True, ""))
    @mock.patch("remote.SlurmRemote.cancel_job", return_value=None)
    def test_cancel_job(self, test_cancel_job, test_run_command):
        self.__gateway.reset()
        self.__gateway.request_remote("Random", "slurm")
        self.assertTrue(
                self.__gateway.cancel("Random", "RANDOM_JOB_ID") == None)

    @mock.patch("remote.Remote.run_command", return_value=(True, ""))
    @mock.patch("remote.SlurmRemote.tail_log", return_value="LOG")
    def test_tail_log(self, test_tail_log, test_run_command):
        self.__gateway.reset()
        self.__gateway.request_remote("Random", "slurm")
        self.assertTrue(self.__gateway.tail_log("Random", "RANDOM_JOB_ID",
            "RANDOM_WORK_DIR") == "LOG")
