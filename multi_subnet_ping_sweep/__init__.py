import functools
import ipaddress
import json
import logging

from multi_subnet_ping_sweep.subnet import ping_subnets
from multi_subnet_ping_sweep.utils import validate_cidr, filter_hosts, set_global_retry

__version__ = "0.0.1"

DEBUG = False
EXCEPTIONS = False
LOGGER = None


def _debug(*args, **kwargs):
    def get_logger():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        cout_handler = logging.StreamHandler()
        cout_handler.setLevel(logging.DEBUG)
        cout_handler.setFormatter(formatter)
        logger.addHandler(cout_handler)
        logger.debug("multi_subnet_ping_sweep Version: {}".format(__version__))
        logger.debug("LOGGER: {}".format(logger))
        return logger

    if not DEBUG:
        return None
    global LOGGER
    LOGGER = LOGGER or get_logger()
    message = " ".join(str(item) for item in args)
    LOGGER.debug(message)


def _raise(err):
    if EXCEPTIONS:
        raise err


def _func_logger(func: callable) -> callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pargs = ", ".join(str(arg) for arg in args)
        kargs = str(kwargs) if kwargs else ""
        all_args = ", ".join((pargs, kargs)) if (pargs and kargs) else (pargs or kargs)
        _debug("Function called:", "{func.__name__}({})".format(all_args, func=func))
        func_return = func(*args, **kwargs)
        _debug("Function returned:", "{func.__name__} -> {rtrn}".format(func=func, rtrn=func_return))
        return func_return

    return wrapper


@_func_logger
def two_subnet_ping_sweep(
        subnet1: str, subnet2: str, retries: int = 1, ignore_list=None, **kwargs
):
    if ignore_list is None:
        ignore_list = []
    try:
        if validate_cidr(subnet1) and validate_cidr(subnet2):
            subnet1 = ipaddress.ip_network(subnet1)
            subnet2 = ipaddress.ip_network(subnet2)
            _debug(f"Subnet 1: {subnet1}")
            _debug(f"Subnet 2: {subnet2}")
        else:
            _debug("Unable to process subnets")
    except ValueError:
        raise ValueError(
            "Invalid subnet input. Must be in IPv4 format with CIDR notation."
        )
    set_global_retry(retries=retries)
    if ignore_list:
        _debug(f"Ignore List: {ignore_list}")

    output = []
    results = ping_subnets(subnets=[subnet1, subnet2], ignore_list=ignore_list)
    filtered_hosts_1 = filter_hosts(subnet1, ignore_list)
    filtered_hosts_2 = filter_hosts(subnet2, ignore_list)
    for host1, host2 in zip(filtered_hosts_1, filtered_hosts_2):
        key1 = str(host1)
        key2 = str(host2)
        if results[subnet1][key1] != results[subnet2][key2]:
            output.append({
                key1: results[subnet1][key1],
                key2: results[subnet2][key2]
            })
    return json.dumps(output)
