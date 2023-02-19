import json

import multiprocessing
import sys
from typing import Dict, List
import asyncio
import platform
from ipaddress import IPv4Address, ip_network

from aioretry import retry
from asyncio import get_event_loop
from asyncio import Lock as AsyncLock

from multi_subnet_ping_sweep.utils import retry_policy

from loguru import logger

logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="ERROR")


@retry(retry_policy)
# @logger.catch
async def ping(host: IPv4Address, shared_results: Dict[str, bool], asyncio_lock: AsyncLock) -> None:
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
    is_alive = proc.returncode == 0
    async with asyncio_lock:
        shared_results[str(host)] = is_alive
        # logger.info(f"Writing ping response from {host}")


# @logger.catch
async def ping_hosts(hosts: List[IPv4Address], shared_results: Dict[str, bool], asyncio_lock: AsyncLock) -> None:
    loop = get_event_loop()
    tasks = [loop.create_task(ping(host, shared_results, asyncio_lock)) for host in hosts]
    await asyncio.gather(*tasks)
    logger.info(f"Gathered ping responses from ping_hosts")


if __name__ == '__main__':
    import timeit

    manager = multiprocessing.Manager()
    results = manager.dict()
    lock = asyncio.Lock()


    def run_func():
        asyncio.run(
            ping_hosts(hosts=list(ip_network("192.168.4.0/24").hosts()), shared_results=results, asyncio_lock=lock))


    time_taken = timeit.timeit(run_func, number=1)
    print(f"Time taken to ping 192.168.4.0/24 hosts: {time_taken}")
    print(f"Response for all ip_addresses {json.dumps(results.copy())}")
