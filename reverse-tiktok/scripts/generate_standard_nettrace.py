
outpath = "../traces/net-flat/"

def make_traces(throughput):
    packets = throughput * 1000 * 1000 / 8 / 1500

    ret_arr = [0] * (720 * 1000)
    npacts = packets / 1000


    for i in range(1, len(ret_arr)):
        ret_arr[i] = int(npacts * i) - int(npacts * (i-1))

    fd = open(f"{outpath}trace-{throughput:.1f}.down", "w")
    for i in range(len(ret_arr)):
        for j in range(ret_arr[i]):
            fd.write(str(i))
            fd.write("\n")
    fd.close()

network_tp_list = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0]

for throughput in network_tp_list:
    make_traces(throughput)