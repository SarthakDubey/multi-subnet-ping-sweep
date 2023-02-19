from multi_subnet_ping_sweep import sweep_two
import timeit

if __name__ == '__main__':
    def test_func():
        result = sweep_two(
            subnet1="192.168.4.0/24",
            subnet2="192.168.10.0/24",
            retries=1,
            ignore_list=[1, 5, 280]
        )
        print(result)
    time_taken = timeit.timeit(test_func, number=1)
    print(f"Time taken: {time_taken} seconds")