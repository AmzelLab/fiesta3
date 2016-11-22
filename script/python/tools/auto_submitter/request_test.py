"""Simple unit tests implementation on request objects"""

import unittest
from unittest import mock
from unittest.mock import MagicMock

from manager import Labor
from request import GeneralRequest
from request import RemoteCommandRequest
from request import RequestRemoteRequest
from request import ResetNetworkRequest
from request import CancelJobRequest

from remote import Remote
from remote import SlurmRemote

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class TestRequest(unittest.TestCase):
    """Test cases for Request objects"""

    def setUp(self):
        """setup some common object for testing"""
        self.__labor = Labor(1)

    def test_general_request(self):
        """Testing general request with some trivial tasks"""

        # Task 1
        request = GeneralRequest(lambda x, y: x + y, 1, 2)
        result = request.action()(*request.args())
        self.assertEqual(result, 3)

        # Task 2
        request = GeneralRequest(lambda: 3)
        result = request.action()(*request.args())
        self.assertEqual(result, 3)

    def test_general_request_with_labor(self):
        """Testing how general request interacts with labor"""

        request = GeneralRequest(lambda x, y: x + y, 1, 2)
        callback = lambda f: self.assertEqual(f.result(), 3)
        self.__labor.perform(request, callback)

    def test_run_multiple_general_with_labor(self):
        """Testing how multiple requests run by the labor force"""

        requests = [
            GeneralRequest(lambda x, y: x + y, 1, 2),
            GeneralRequest(lambda: 3),
            GeneralRequest(lambda x: x + 1, 2)
        ]
        callback = lambda f: self.assertEqual(f.result(), 3)

        for request in requests:
            self.__labor.perform(request, callback)

        callback = lambda f: self.assertNotEqual(f.result(), 2)

        for request in requests:
            self.__labor.perform(request, callback)

    def test_make_network_requests(self):
        """Testing whether network request objects are correctly
        made."""
        remote_server = "RANDOM"
        request = RequestRemoteRequest(remote_server, "slurm")
        self.assertEqual(list(request.args()), [remote_server, "slurm"])

    @mock.patch('remote.check_output')
    def test_remote_command_with_labor(self, mock_check_output):
        """Testing remote command request"""

        mock_check_output.return_value = b'LS'
        remote_server = "RANDOM"
        request = RequestRemoteRequest(remote_server, "slurm")

        def callback(f_result):
            self.assertEqual(f_result.result(), True)

        self.__labor.perform(request, callback)

    @mock.patch('remote.check_output', MagicMock(return_value=b"LS"))
    def test_cancel_job_with_labor(self):
        """Testing remote command request"""

        remote_server = "RANDOM"
        request = RequestRemoteRequest(remote_server, "slurm")

        def callback(f_result):
            self.assertEqual(f_result.result(), True)
            request = CancelJobRequest(remote_server, "RANDOM")
            self.__labor.perform(request)

        self.__labor.perform(request, callback)
