"""Unit tests for specialist.py
"""

import unittest
from unittest import mock

from manager import Labor
from specialist import SpecialistFactory
from specialist import GromacsSpecialist

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class TestSpecialist(unittest.TestCase):
    """Test Cases for Specialist"""

    def setUp(self):
        """setup some common object for testing"""
        # Mock a labor object here
        patcher = mock.patch('manager.Labor')
        self.__mock_class = patcher.start()
        self.addCleanup(patcher.stop)

        self.__labor = self.__mock_class()
        self.__gromacs_spec = SpecialistFactory.create_specialist_with_labor(
            "Gromacs", self.__labor)

    def test_create_unknown_specialist(self):
        """Testing creating unknown specialist"""
        none_spec = SpecialistFactory.create_specialist_with_labor(
            "ANYTHING", None)
        self.assertEqual(none_spec, None)

    def test_create_existing_specialist(self):
        """Testing creating registered specialist"""
        for ftype in SpecialistFactory.SPECIALIST_TYPE:
            spec = SpecialistFactory.create_specialist_with_labor(
                ftype, None)
            self.assertNotEqual(spec, None)

    def test_gromacs_job_with_incorrect_meta(self):
        """Testing adding Gromacs job with incorrect meta data"""
        job = {}
        job["nameBase"] = "ANYTHING"
        job["name"] = "ANYTHING"
        result = self.__gromacs_spec.add_job(job)
        self.assertFalse(result)

    def test_gromacs_job_with_correct_meta(self):
        """Testing adding Gromacs job with correct meta"""
        job = {}
        job["name"] = "ANYTHING"
        for key in GromacsSpecialist.REQUIRED:
            job[key] = "ANYTHING"

        result = self.__gromacs_spec.add_job(job)
        self.assertTrue(result)

    def test_add_duplicate_gromacs_job(self):
        """Testing adding duplicate Gromacs job"""
        job_one = {}
        job_two = {}

        job_one["name"] = "ANYTHING"
        job_two["name"] = "ANYTHING"

        for key in GromacsSpecialist.REQUIRED:
            job_one[key] = "ANYTHING"
            job_two[key] = "ANYTHING"

        result = self.__gromacs_spec.add_job(job_one)
        self.assertTrue(result)

        result = self.__gromacs_spec.add_job(job_two)
        self.assertFalse(result)
