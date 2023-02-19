import unittest
from ipaddress import ip_network

from multi_subnet_ping_sweep.utils import validate_cidr, filter_hosts


class TestValidateCIDR(unittest.TestCase):

    def test_valid_cidr(self):
        self.assertTrue(validate_cidr('192.0.2.0/24'))
        self.assertTrue(validate_cidr('10.0.0.0/8'))
        self.assertTrue(validate_cidr('172.16.0.0/12'))
        self.assertTrue(validate_cidr('192.168.0.0/16'))

    def test_invalid_cidr_format(self):
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0/24/32')
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0:24')
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0')
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0/')

    def test_invalid_cidr_prefix_length(self):
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0/33')
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0/-1')
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0/a')

    def test_invalid_ip_address(self):
        with self.assertRaises(ValueError):
            validate_cidr('256.0.2.0/24')
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0.1/24')
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2./24')
        with self.assertRaises(ValueError):
            validate_cidr('192.0.2.0/-1')
