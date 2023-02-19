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
        asyncio_lock = asyncio.Lock()
        shared_result = {}
        await ping(IPv4Address('8.8.8.8'), asyncio_lock=asyncio_lock, shared_results=shared_result)
        self.assertEqual(shared_result, {'8.8.8.8': True})

    async def test_invalid_ip(self):
        with self.assertRaises(ValueError):
            await ping(IPv4Address('invalid'))

    async def test_unreachable_ip(self):
        shared_result = {}
        asyncio_lock = asyncio.Lock()
        await ping(IPv4Address('10.0.0.1'), asyncio_lock=asyncio_lock, shared_results=shared_result)
        self.assertEqual(shared_result, {'10.0.0.1': False})


class TestPingHosts(unittest.TestCase):
    @patch("asyncio.create_subprocess_shell")
    @pytest.mark.asyncio
    def test_ping_hosts_with_single_host(self, create_subprocess_shell: MagicMock):
        proc = AsyncMock()
        proc.returncode = 0
        proc.communicate.return_value = (b'', b'')
        create_subprocess_shell.return_value = proc
        hosts = [IPv4Address('192.0.2.1')]
        shared_result = {}
        asyncio_lock = asyncio.Lock()
        asyncio.run(ping_hosts(hosts, asyncio_lock=asyncio_lock, shared_results=shared_result))
        self.assertEqual(len(shared_result), 1)
        self.assertIn('192.0.2.1', shared_result)
        self.assertTrue(shared_result['192.0.2.1'])
