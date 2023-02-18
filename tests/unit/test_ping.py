import unittest
import asyncio
from ipaddress import IPv4Address
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from multi_subnet_ping_sweep.ping import ping_hosts, ping


class TestPing(unittest.IsolatedAsyncioTestCase):
    @patch("asyncio.create_subprocess_shell")
    @pytest.mark.asyncio
    async def test_valid_ip(self, create_subprocess_shell: MagicMock):
        proc = AsyncMock()
        proc.returncode = 0
        proc.communicate.return_value = (b'', b'')
        create_subprocess_shell.return_value = proc
        result = await ping(IPv4Address('8.8.8.8'))
        self.assertEqual(result, {'8.8.8.8': True})

    async def test_invalid_ip(self):
        with self.assertRaises(ValueError):
            await ping(IPv4Address('invalid'))

    async def test_unreachable_ip(self):
        result = await ping(IPv4Address('10.0.0.1'))
        self.assertEqual(result, {'10.0.0.1': False})


class TestPingHosts(unittest.TestCase):
    @patch("multi_subnet_ping_sweep.ping.ping")
    @pytest.mark.asyncio
    def test_ping_hosts_with_single_host(self, ping: AsyncMock):
        ping.return_value = {"192.0.2.1": True}
        hosts = [IPv4Address('192.0.2.1')]
        result = asyncio.run(ping_hosts(hosts))
        self.assertEqual(len(result), 1)
        self.assertIn('192.0.2.1', result)
        self.assertTrue(result['192.0.2.1'])
