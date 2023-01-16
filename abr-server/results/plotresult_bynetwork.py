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



def main(args):

    cnt = 0
    algorithm_list = ["empc", "mpc"]
    probability_models = ["10timesaccurate", "byuser", "byvideo", "equal"]
    # network_traces = os.listdir(args.networktraces)[:2]
    network_traces = ["trace_9284_http---www.msn.com", "trace_10647_http---www.google.com-mobile-", "trace_6420_http---www.ebay.com", "trace_5357_http---www.ebay.com", "trace_5300_http---www.google.com-mobile-", "trace_28652_http---www.youtube.com", "trace_662422_http---edition.cnn.com", "trace_614990_http---www.google.com-mobile-"]
    viewing_traces = os.listdir(args.viewingtraces)

    byalgorithm = {}
    byprobability = {}



    for network_iter in network_traces:

        for algorithm_iter in algorithm_list:
            byalgorithm[algorithm_iter] = []


        for algorithm_iter in algorithm_list:
            for probability_iter in probability_models:
            
                for viewing_iter in viewing_traces:

                    logpath = f"{args.inputpath}/{algorithm_iter}/{probability_iter}/{network_iter}/{viewing_iter}"
                    trace = np.loadtxt(logpath)

                    reward_lists = getreward(trace)

                    cur_reward = np.average(reward_lists)

                    if probability_iter == "byvideo":
                        byalgorithm[algorithm_iter].append(cur_reward)
        
        print(network_iter)

        print(np.average(byalgorithm["empc"]) / np.average(byalgorithm["mpc"]))
        print(np.median(byalgorithm["empc"]) / np.median(byalgorithm["mpc"]))

        print("===========================")

        ecdf_sv = ECDF(byalgorithm["empc"])
        ecdf_mpc = ECDF(byalgorithm["mpc"])

        fig = plt.figure(figsize=(6,3))

        plt.plot(ecdf_sv.x, ecdf_sv.y, label="SVS", lw=3)
        plt.plot(ecdf_mpc.x, ecdf_mpc.y, label="MPC", lw=3)


        plt.xlim(0, 2000)
        plt.ylabel("CDF")
        plt.xlabel("Average QoE")

        plt.legend()
        plt.savefig(f"{network_iter}.png", bbox_inches='tight')
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


