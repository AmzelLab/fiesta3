"""unit test for gateway.py
"""

import unittest
from unittest import mock

from gateway import Gateway

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class TestGateway(unittest.TestCase):
    """Test cases for Gateway"""

    def test_singleton(self):
        """Testing Gateway object is a singleton."""
        gateway_a = Gateway()
        gateway_b = Gateway()
        self.assertTrue(gateway_a == gateway_b)

    def test_direct_actions_with_unregistered(self):
        """Testing Gateway functionality with direct actions only.
        By saying direct actions, we mean actions with no cache."""
        gateway = Gateway()
        output = gateway.submit("RANDOM", "RANDOM", "RANDOM")
        self.assertTrue(output == None)

    def test_direct_actions_with_registered(self):
        """Testing Gateway functionality with direct actions only.
        By saying direct actions, we mean actions with no cache."""
        gateway = Gateway()
        output = gateway.submit("RANDOM", "RANDOM", "RANDOM")
        self.assertTrue(output == None)

