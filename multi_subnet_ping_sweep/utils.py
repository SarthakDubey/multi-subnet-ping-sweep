from loguru import logger
import re
from ipaddress import ip_network, IPv4Address, AddressValueError
from typing import List

from aioretry import RetryInfo, RetryPolicyStrategy


RETRY_POLICY = 1


def set_global_retry(retries: int = 1):
    retries = min(retries, 3)
    global RETRY_POLICY
    RETRY_POLICY = max(RETRY_POLICY, retries)


def validate_cidr(cidr_str):
    # First, check if the input matches the correct CIDR format using regex
    pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if not re.match(pattern, cidr_str):
        raise ValueError('Invalid CIDR notation')

    # If the format is correct, check if the CIDR notation is valid
    cidr_parts = cidr_str.split('/')
    if len(cidr_parts) != 2:
        raise ValueError('Invalid CIDR notation')

    ip_address = cidr_parts[0]
    prefix_length = int(cidr_parts[1])
    if prefix_length < 0 or prefix_length > 32:
        raise ValueError('Invalid CIDR notation')

    # Finally, check if the IP address is valid using built-in functions
    octets = ip_address.split('.')
    if len(octets) != 4:
        raise ValueError('Invalid CIDR notation')

    for octet in octets:
        if not octet.isdigit() or int(octet) < 0 or int(octet) > 255:
            raise ValueError('Invalid CIDR notation')

    return True


def filter_hosts(subnet: ip_network, ignore_list=None) -> List[IPv4Address]:
    if ignore_list is None:
        ignore_list = []
    ignore_hosts = set()
    for octet in ignore_list:
        ignore_hosts.add(int_to_subnet_ip(subnet, octet))
    hosts: List[IPv4Address] = [
        host
        for host in subnet
        if isinstance(host, IPv4Address) and host not in ignore_hosts
    ]
    return hosts


def int_to_subnet_ip(subnet: ip_network, octet: int) -> IPv4Address:
    subnet_split = (str(subnet)).split(".")
    subnet_split[-1] = str(octet)

    try:
        ip_addr = IPv4Address(".".join(subnet_split))
        return ip_addr
    except AddressValueError:
        logger.warning(f"Subnet: {subnet} - Octet {octet} (> 255) not permitted.")


def retry_policy(info: RetryInfo) -> RetryPolicyStrategy:
    return info.fails > RETRY_POLICY, info.fails * 0.1
