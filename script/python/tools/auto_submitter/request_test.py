"""Simple unit tests implementation on request objects"""

import unittest

from manager import Labor
from request import GeneralRequest

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

    def test_run_multiple_requests_with_labor(self):
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
