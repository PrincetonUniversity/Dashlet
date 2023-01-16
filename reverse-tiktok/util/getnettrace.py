import os

foldername = "/home/acer/Downloads/pensieve-master/traces/fcc/mahimahi"
filenames = os.listdir(foldername)

nettp_list = [9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5]

net_name_map = {}

net_name_residual = {}


for nettp in nettp_list:
    net_name_residual[nettp] = 50000


def gettp(fname):
    throughput = 0
    with open(fname) as f:
        lines = f.readlines()
        first_packet_time = int(lines[0])
        last_packet_time = int(lines[-1])

        throughput = len(lines) * 1500 * 8 / 1000 / (last_packet_time - first_packet_time)

    return throughput

count = 0
for fname in filenames:
    first_packet_time = 0
    last_packet_time = 0

    throughput = gettp(f"{foldername}/{fname}")

    print(throughput)

    low_bound = int(throughput)

    iterlist = [low_bound + 0.0, low_bound + 0.5, low_bound + 1.0]

    for nettp in iterlist:
        if nettp >= nettp_list[0] and nettp < nettp_list[-1]:

            diff = abs(nettp - throughput)

            if diff < net_name_residual[nettp]:
                net_name_residual[nettp] = diff
                net_name_map[nettp] = fname
    count += 1

    if count % 100 == 0:
        print(count)
        print(net_name_map)
        print(net_name_residual)


for tp in nettp_list[1:(len(nettp_list) - 1)]:
    throughput = gettp(f"{foldername}/{net_name_map[tp]}")
    print(throughput)

    cmd = f"cp {foldername}/{net_name_map[tp]} ../traces/network/"
    print(cmd)
    os.system(cmd)

    cmd = f"mv ../traces/network/{net_name_map[tp]} ../traces/network/trace-{tp:.1f}.down"
    print(cmd)
    os.system(cmd)