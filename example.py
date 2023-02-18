from multi_subnet_ping_sweep import two_subnet_ping_sweep

result = two_subnet_ping_sweep(
    subnet1="192.168.4.0/24",
    subnet2="192.168.10.0/24",
    retries=1,
    ignore_list=[1, 5, 10]
)
print(result)