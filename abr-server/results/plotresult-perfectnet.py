import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
import time
import os
import argparse
plt.rcParams.update({'font.size': 14})


from statsmodels.distributions.empirical_distribution import ECDF


bitraterewards = [1143, 2064, 4449, 6086, 9193, 0]
chunklength = 5.00

penalty_weight = 9193


def getreward(trace):
    reward_list = []
    for i in range(len(trace)):
        reward = bitraterewards[int(trace[i][1])] - penalty_weight * trace[i][0]
        reward_list.append(reward)

    return reward_list

# trace_normal = np.loadtxt("../cooked-empc.log")
# trace_acc = np.loadtxt("../cooked-empcacc.log")
# trace_short = np.loadtxt("../cooked-empcshort.log")
# 
# 
# reward_normal = getreward(trace_normal)
# reward_acc = getreward(trace_acc)
# reward_short = getreward(trace_short)
# 
# ecdf_normal = ECDF(reward_normal)
# ecdf_acc = ECDF(reward_acc)
# ecdf_short = ECDF(reward_short)
# 
# fig = plt.figure(figsize=(6,3))
# 
# plt.plot(ecdf_normal.x, ecdf_normal.y, label="eMPC", lw=3)
# plt.plot(ecdf_acc.x, ecdf_acc.y, label="eMPC-accuracy", lw=3)
# 
# 
# plt.xlim(0, 2000)
# plt.ylabel("CDF")
# plt.xlabel("Chunk reward")
# 
# plt.legend()
# # plt.title("%d Edge server"%(i+1))
# plt.savefig("result1.png", bbox_inches='tight')
# plt.close()
# 
# 
# 
# fig = plt.figure(figsize=(6,3))
# 
# plt.plot(ecdf_normal.x, ecdf_normal.y, label="eMPC", lw=3)
# plt.plot(ecdf_short.x, ecdf_short.y, label="eMPC-Heu", lw=3)
# 
# plt.xlim(0, 2000)
# plt.ylabel("CDF")
# plt.xlabel("Chunk reward")
# 
# plt.legend()
# # plt.title("%d Edge server"%(i+1))
# plt.savefig("result2.png", bbox_inches='tight')
# plt.close()


def process_trace(algorithm_iter, probability_iter, network_traces, viewing_traces):
    ret = []

    for network_iter in network_traces:
        for viewing_iter in viewing_traces:

            logpath = f"{args.inputpath}/{algorithm_iter}/{probability_iter}/{network_iter}/{viewing_iter}"
            trace = np.loadtxt(logpath)

            reward_lists = getreward(trace)

            cur_reward = np.average(reward_lists)

            ret.append(cur_reward)

    return ret
def main(args):

    cnt = 0
    algorithm_list = ["empc"]
    probability_models = ["byvideo"]
    # network_traces = os.listdir(args.networktraces)[:2]
    # network_traces = ["trace_6420_http---www.ebay.com"]
    network_traces = ["trace_9284_http---www.msn.com", "trace_10647_http---www.google.com-mobile-", "trace_6420_http---www.ebay.com", "trace_5357_http---www.ebay.com", "trace_5300_http---www.google.com-mobile-", "trace_28652_http---www.youtube.com", "trace_662422_http---edition.cnn.com", "trace_614990_http---www.google.com-mobile-"]
    viewing_traces = os.listdir(args.viewingtraces)

    svs_trace = process_trace("empc", "byvideo", network_traces, viewing_traces)
    oracle_trace = process_trace("oracle", "full_accuracy", network_traces, viewing_traces)
    perfect_net = process_trace("oracle", "byvideo", network_traces, viewing_traces)
    perfect_swipe = process_trace("empc", "full_accuracy", network_traces, viewing_traces)






    ecdf_sv = ECDF(svs_trace)
    ecdf_oracle = ECDF(oracle_trace)
    ecdf_net = ECDF(perfect_net)
    ecdf_swipe = ECDF(perfect_swipe)

    print("====================")
    print(np.median(svs_trace) / np.median(oracle_trace))
    print(np.average(svs_trace) / np.average(oracle_trace))

    print("====================")
    print(np.median(perfect_net) / np.median(oracle_trace))
    print(np.average(perfect_net) / np.average(oracle_trace))


    print("====================")
    print(np.median(perfect_swipe) / np.median(oracle_trace))
    print(np.average(perfect_swipe) / np.average(oracle_trace))

    fig = plt.figure(figsize=(6, 3))

    plt.plot(ecdf_sv.x, ecdf_sv.y, label="SVS", lw=3)
    plt.plot(ecdf_oracle.x, ecdf_oracle.y, label="Oracle", lw=3)
    plt.plot(ecdf_net.x, ecdf_net.y, label="Perfect Net", lw=3)
    plt.plot(ecdf_swipe.x, ecdf_swipe.y, label="Perfect Swipe", lw=3)


    plt.xlim(0, 10000)
    plt.ylabel("CDF")
    plt.xlabel("Average QoE")

    plt.legend()
    plt.savefig("result3.png", bbox_inches='tight')
    plt.close()





    print(cnt)

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewingtraces', default='/home/acer/Documents/ttstream/testing/dataclean/data', help='Viewing trace path')
    parser.add_argument('--networktraces', default='/home/acer/Downloads/pensieve-master/traces/fcc/mahimahi', help='The id to sequence number mapping')
    parser.add_argument('--inputpath', default='/home/acer/Documents/ttstream/run/cooked-sim', help='The path to save processed data')
    # parser.add_argument('--inputpath', default='/home/acer/Documents/ttstream/run/result-sim', help='The path to save processed data')

    args = parser.parse_args()
    main(args)


