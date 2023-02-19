import asyncio
import ipaddress
import multiprocessing
import sys

from loguru import logger

from multi_subnet_ping_sweep.subnet import ping_subnets
from multi_subnet_ping_sweep.utils import validate_cidr, set_global_retry

logger.add(sys.stderr, format="{time} {level} {message}", level="WARNING")

__version__ = "0.0.1"
DEBUG = False
EXCEPTIONS = False
LOGGER = None


def sweep_two(
        subnet1: str, subnet2: str, retries: int = 1, ignore_list=None, **kwargs
):
    if ignore_list is None:
        ignore_list = []
    try:
        if validate_cidr(subnet1) and validate_cidr(subnet2):
            subnet1 = ipaddress.ip_network(subnet1)
            subnet2 = ipaddress.ip_network(subnet2)
            logger.debug(f"Subnet 1: {subnet1}")
            logger.debug(f"Subnet 2: {subnet2}")
        else:
            logger.debug("Unable to process subnets")
    except ValueError:
        raise ValueError(
            "Invalid subnet input. Must be in IPv4 format with CIDR notation."
        )
    set_global_retry(retries=retries)
    if ignore_list:
        logger.debug(f"Ignore List: {ignore_list}")

    output = []

    with multiprocessing.Manager() as manager:
        lock = manager.Lock()
        async_lock = asyncio.Lock()
        results = manager.dict()

        ping_subnets(
            subnets=[subnet1, subnet2],
            shared_results=results,
            thread_lock=lock,
            asyncio_lock=async_lock,
            ignore_list=ignore_list
        )

        # results = ping_subnets(subnets=[subnet1, subnet2], ignore_list=ignore_list)
        filtered_hosts_1 = str(subnet1) + " filtered hosts"
        filtered_hosts_2 = str(subnet2) + " filtered hosts"

        for host1, host2 in zip(results[filtered_hosts_1], results[filtered_hosts_2]):
            try:
                if results[host1] != results[host2]:
                    output.append({
                        host1: results[host1],
                        host2: results[host2]
                    })
            except KeyError as e:
                logger.error(e)

        return output
