# from multi_subnet_ping_sweep import sweep_two
import json
import timeit

import multi_subnet_ping_sweep

if __name__ == '__main__':
    def test_func():
        result = multi_subnet_ping_sweep.sweep_two(
            subnet1="192.168.4.0/24",
            subnet2="192.168.10.0/24",
            retries=1,
            ignore_list=[1, 5, 280]
        )
        print(json.dumps(result, indent=1))
    time_taken = timeit.timeit(test_func, number=1)
    print(f"Time taken: {time_taken} seconds")
