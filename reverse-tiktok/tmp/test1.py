import numpy as np
import matplotlib.pyplot as plt



def make_traces(throughput):
    packets = throughput * 1000 * 1000 / 8 / 1500

    ret_arr = [0] * (100 * 1000)
    npacts = packets / 1000


    for i in range(1, len(ret_arr)):
        ret_arr[i] = int(npacts * i) - int(npacts * (i-1))

    fd = open(f"throughput_{throughput}.txt", "w")
    for i in range(len(ret_arr)):
        for j in range(ret_arr[i]):
            fd.write(str(i))
            fd.write("\n")

import random

def make_traces_random(throughput):
    packets = throughput * 1000 * 1000 / 8 / 1500

    ret_arr = [0] * (100 * 1000)
    npacts = packets / 1000


    total_packet = int(npacts * len(ret_arr))
    send_seconds = []
    for i in range(total_packet):
        send_seconds.append(random.randint(0, len(ret_arr)))


    send_seconds = sorted(send_seconds)
    tmp = 1

    # for i in range(1, len(ret_arr)):
    #     ret_arr[i] = int(npacts * i) - int(npacts * (i-1))
    #
    fd = open(f"throughput_{throughput}_rand.txt", "w")
    for i in range(len(send_seconds)):
        fd.write(str(send_seconds[i]))
        fd.write("\n")

make_traces_random(1)