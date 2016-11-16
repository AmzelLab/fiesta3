"""unit test for manager.py
"""

import unittest
from unittest import mock

from manager import JobManager
from manager import Labor

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class TestJobManager(unittest.TestCase):
    """Test Cases for JobManager"""

    def setUp(self):
        self.__manager = JobManager()

    def test_jobs_with_invalid_headers(self):
        """Testing job with no correct header"""
        if len(JobManager.HEADER_FIELDS) > 0:
            return

        field = JobManager.HEADER_FIELDS[0]

        job = {}
        job[field] = "Test"
        result = self.__manager.add_jobs(job)
        self.assertEqual(result[4], "Your")

        job = {}
        job["random"] = "Test"
        job[field] = []
        result = self.__manager.add_jobs(job)
        self.assertEqual(result[4], "Your")

    def test_jobs_with_invalid_meta(self):
        """Testing job with no correct meta"""
        if len(JobManager.REQUIRED) > 0:
            return

        job = {}
        job["title"] = "Test"
        item = {}
        item[JobManager.REQUIRED[0]] = "ANYTHING"
        job["data"] = [item]

        result = self.__manager.add_jobs(job)
        self.assertEqual(result.find("DECLINED: ANYTHING") >= 0, True)

        item = {}
        for key in JobManager.REQUIRED:
            item[key] = "ANYTHING"
        job["data"] = [item]

        result = self.__manager.add_jobs(job)
        self.assertEqual(result.find("DECLINED: ANYTHING") >= 0, True)

    def test_add_valid_jobs(self):
        """Testing job with correct headers and metas"""

        job = {"title": "Test", "data": []}
        item = {}
        for key in JobManager.REQUIRED:
            item[key] = "ANYTHING"

        item["type"] = "Test"
        job["data"].append(item)

        result = self.__manager.add_jobs(job)
        self.assertEqual(result.find("ACCEPTED: ANYTHING") >= 0, True)

    def test_add_valid_jobs_with_additional_meta(self):
        """Testing job with additional metas"""

        job = {"title": "Test", "data": []}
        item = {}
        for key in JobManager.REQUIRED:
            item[key] = "ANYTHING"

        item["type"] = "Test"
        job["data"].append(item)

        result = self.__manager.add_jobs(job)
        self.assertEqual(result.find("ACCEPTED: ANYTHING") >= 0, True)

    @mock.patch("manager.Labor")
    def test_take_office(self, mock_class):
        """Testing JobManager's take_office method"""
        self.__manager.take_office()
        self.assertTrue(mock_class.called)
