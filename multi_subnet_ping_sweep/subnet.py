import asyncio
import json
import sys

from loguru import logger
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from ipaddress import ip_network
from threading import Lock
from typing import Any, Dict, List

from asyncio import Lock as AsyncLock

from multi_subnet_ping_sweep.ping import ping_hosts
from multi_subnet_ping_sweep.utils import filter_hosts

logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="ERROR")


def ping_hosts_asyncio_lock_shared_memory(
        subnet: ip_network, shared_results: Dict[str, Any], asyncio_lock: AsyncLock
) -> None:
    subnet_key = str(subnet)
    subnet_string = subnet_key + " filtered hosts"
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ping_hosts(hosts=shared_results[subnet_string], shared_results=shared_results,
                                       asyncio_lock=asyncio_lock))
    logger.debug(f'Successfully completed pings for: {subnet}')


def filter_hosts_from_subnet(subnet: ip_network, shared_results: Dict[str, Any], thread_lock, ignore_list=None):
    if ignore_list is None:
        ignore_list = []
    subnet_string = str(subnet) + " filtered hosts"
    with thread_lock:
        shared_results[subnet_string] = filter_hosts(subnet=subnet, ignore_list=ignore_list)
        logger.debug(f'Successfully completed host filtering for: {subnet}')


def ping_subnets(
        subnets: List[ip_network], shared_results: Dict[str, Any], thread_lock: Lock, asyncio_lock: AsyncLock,
        ignore_list=None
) -> None:
    if ignore_list is None:
        ignore_list = []

    generate_hosts = partial(
        filter_hosts_from_subnet,
        shared_results=shared_results,
        thread_lock=thread_lock,
        ignore_list=ignore_list
    )

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(generate_hosts, subnets)

    # response = {}
    generate_pings = partial(
        ping_hosts_asyncio_lock_shared_memory,
        shared_results=shared_results,
        asyncio_lock=asyncio_lock
    )

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(generate_pings, subnets)

    for subnet in subnets:
        subnet_string = str(subnet) + " filtered hosts"
        shared_results[subnet_string] = [str(host) for host in shared_results[subnet_string]]


if __name__ == '__main__':
    import timeit

    manager = multiprocessing.Manager()
    results = manager.dict()
    lock = manager.Lock()
    async_lock = asyncio.Lock()


    def run_func():
        ping_subnets(
            subnets=[ip_network("192.168.4.0/24"), ip_network("192.168.10.0/24")],
            thread_lock=lock,
            asyncio_lock=async_lock,
            shared_results=results)


    time_taken = timeit.timeit(run_func, number=1)
    print(f"Time taken to ping sweep 192.168.4.0/24 and 192.168.10.0/24: {time_taken}")
    print(f"Response for all subnets {json.dumps(results.copy())}")
