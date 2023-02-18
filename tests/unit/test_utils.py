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


class TestFilterHosts(unittest.TestCase):

    def test_empty_subnet(self):
        subnet = ip_network('10.0.0.0/32')
        ignore_list = [1, 2, 3]
        self.assertEqual(filter_hosts(subnet, ignore_list), [])

    def test_ignore_all_hosts(self):
        subnet = ip_network('192.168.0.0/24')
        ignore_list = [i for i in range(1, 256)]
        self.assertEqual(filter_hosts(subnet, ignore_list), [])

    def test_no_ignored_hosts(self):
        subnet = ip_network('172.16.0.0/16')
        self.assertEqual(filter_hosts(subnet), list(subnet.hosts()))

    def test_some_ignored_hosts(self):
        subnet = ip_network('192.168.1.0/24')
        ignore_list = [1, 2, 3, 10, 20, 30, 200, 220, 240]
        expected_hosts = [host for host in subnet.hosts() if int(host) not in ignore_list]
        self.assertEqual(filter_hosts(subnet, ignore_list), expected_hosts)

    def test_ignore_list_is_none(self):
        subnet = ip_network('10.0.0.0/8')
        self.assertEqual(filter_hosts(subnet), list(subnet.hosts()))

    def test_ignore_list_has_duplicates(self):
        subnet = ip_network('172.16.0.0/12')
        ignore_list = [1, 2, 3, 10, 20, 30, 200, 220, 240, 10, 20, 30]
        expected_hosts = [host for host in subnet.hosts() if int(host) not in ignore_list]
        self.assertEqual(filter_hosts(subnet, ignore_list), expected_hosts)