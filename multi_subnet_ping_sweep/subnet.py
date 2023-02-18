import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from ipaddress import ip_network
from typing import Any, Dict, List

from multi_subnet_ping_sweep.ping import ping_hosts
from multi_subnet_ping_sweep.utils import filter_hosts
logger = logging.getLogger(__name__)


def ping_filter_subnet_hosts(
    subnet: ip_network, ignore_list=None
) -> Dict[str, Any]:
    if ignore_list is None:
        ignore_list = []
    hosts = filter_hosts(subnet=subnet, ignore_list=ignore_list)
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(ping_hosts(hosts))
    return result


def ping_subnets(
    subnets: List[ip_network], ignore_list=None
) -> Dict[str, Any]:
    if ignore_list is None:
        ignore_list = []
    response = {}
    func = partial(ping_filter_subnet_hosts, ignore_list=ignore_list)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(func, subnets)
        for subnet, result in enumerate(results):
            logger.info(f"Collecting response from subnet: {subnets[subnet]}")
            response[subnets[subnet]] = result
    return response
