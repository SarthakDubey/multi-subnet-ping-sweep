from typing import Dict, List, Any
import asyncio
import platform
from ipaddress import IPv4Address

from aioretry import retry

from multi_subnet_ping_sweep.utils import retry_policy


@retry(retry_policy)
async def ping(host: IPv4Address) -> dict[Any, Any]:
    if platform.system().lower() == "windows":
        ping_args = ["ping", str(host), "-n", "1", "-w", "500"]
    else:
        ping_args = ["ping", str(host), "-c", "1", "-W", "1"]
    proc = await asyncio.create_subprocess_shell(
        " ".join(ping_args),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return {str(host): proc.returncode == 0}


async def ping_hosts(hosts: List[IPv4Address]) -> Dict[str, Any]:
    tasks = [asyncio.create_task(ping(host)) for host in hosts]
    results = {}
    for task in asyncio.as_completed(tasks):
        results |= await task
    return results
