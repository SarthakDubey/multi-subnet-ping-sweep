import argparse
import multi_subnet_ping_sweep


def main(assigned_args: list = None):
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(
        prog="multi_subnet_ping_sweep",
        description="A python program to ping multiple subnets in multi-threaded, asyncio way!")

    parser.add_argument("-v", "--version", action="version", version=multi_subnet_ping_sweep.__version__)
    parser.add_argument("-s1", "--subnet1", dest="subnet1",  metavar="SUBNET_1", default="192.168.0.0", type=str,
                        help="Description of Subnet 1")
    parser.add_argument("-s2", "--subnet2", dest="subnet2", metavar="SUBNET_2", default="192.168.1.0", type=str,
                        help="Description of Subnet 2")
    parser.add_argument("-r", "--retries", dest="retries", type=int, default=1, help="Number of retries, on each ping")
    parser.add_argument("-i", "--ignore_list", dest="ignore_list", type=list, nargs="*", default="",
                        help="Delimited list of octets to ignore")
    parser.add_argument("-D", "--debug", action="store_true", dest="debug", help="Turn on DEBUG mode.")
    parser.add_argument("-E", "--exceptions", action="store_true", dest="exceptions", help="Turn on EXCEPTIONS mode.")

    # Parse the command line arguments
    args = parser.parse_args(assigned_args)
    multi_subnet_ping_sweep.DEBUG = args.debug
    multi_subnet_ping_sweep.EXCEPTIONS = args.exceptions
    # Call the main function with the command line arguments as keyword arguments
    try:
        multi_subnet_ping_sweep.sweep_two(
            subnet1=args.subnet1,
            subnet2=args.subnet2,
            retries=args.retries,
            ignore_list=args.ignore_list
        )
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
