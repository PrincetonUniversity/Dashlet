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


chunklength = 5.00
penalty_weight = 700 * 5


dashlet_folder = "/home/acer/Documents/ttstream/run/cooked-sim/dashlet"
tt_folder = "/home/acer/Documents/reverse-tiktok/plot/qoe"


def get_reward_dashlet(data):
    ret = [0 for i in range(80)]
    rebuffer = [0 for i in range(80)]
    bitrwate_reward = [0 for i in range(80)]
    for i in range(len(data)):
        idx = int(data[i][2])

        if idx > 80:
            continue

        ret[idx] += (data[i][1] - data[i][0] * penalty_weight)
        rebuffer[idx] += data[i][0]
        bitrwate_reward[idx] += data[i][1]

    return np.array(ret), rebuffer, bitrwate_reward

def get_reward_tt(data):
    ret = [0 for i in range(80)]
    rebuffer = [0 for i in range(80)]
    bitrwate_reward = [0 for i in range(80)]
    for i in range(len(data)):
        ret[i] += (data[i][1] - data[i][0] * penalty_weight)
        rebuffer[i] += data[i][0]
        bitrwate_reward[i] += data[i][1]

    return np.array(ret), rebuffer, bitrwate_reward

total_dashlet = []
total_tt = []
total_opt = []

rebuffer_dashlet_dis = []
rebuffer_tt_dis = []


bitrate_reward_dashlet_dis = []
bitrate_reward_tt_dis = []
bitrate_reward_opt_dis = []

by_throughput_dashlet = {}
by_throughput_tt = {}


for network_idx in range(6, 20):
    network_tp = network_idx / 2.0

    if int(network_tp) not in by_throughput_dashlet.keys():
        by_throughput_dashlet[int(network_tp)] = []
        by_throughput_tt[int(network_tp)] = []

    for swipe_idx in range(2, 6):
        testname = f"trace-{network_tp:.1f}-swipe-{swipe_idx}"

        fname_dashlet = f"{dashlet_folder}/{testname}.txt"
        fname_tt = f"{tt_folder}/{testname}.txt"

        fname_opt = f"{dashlet_folder}/{testname}-b.txt"

        data_dashlet = np.loadtxt(fname_dashlet)
        data_tt = np.loadtxt(fname_tt)
        data_opt = np.loadtxt(fname_opt)

        processed_dashlet, rebuffer_dashlet, bitrwate_reward_dashlet = get_reward_dashlet(data_dashlet)
        processed_opt, rebuffer_opt, bitrwate_reward_opt = get_reward_dashlet(data_opt)

        processed_tt, rebuffer_tt, bitrwate_reward_tt = get_reward_tt(data_tt)


        for i in range(1, 7):
            val_dashlet = np.average(processed_dashlet[i*10:(i+1)*10])
            val_tt = np.average(processed_tt[i*10:(i+1)*10])
            val_opt = np.average(processed_opt[i*10:(i+1)*10])

            if val_tt > -1000:
            # if True:
                total_dashlet.append(val_dashlet)
                total_tt.append(val_tt)
                total_opt.append(val_opt)

                by_throughput_dashlet[int(network_tp)].append(val_dashlet)
                by_throughput_tt[int(network_tp)].append(val_tt)

                rebuffer_dashlet_dis.append(np.sum(rebuffer_dashlet[i*10:(i+1)*10]))
                rebuffer_tt_dis.append(np.sum(rebuffer_tt[i*10:(i+1)*10]))

                bitrate_reward_dashlet_dis.append(np.average(bitrwate_reward_dashlet[i*10:(i+1)*10]))
                bitrate_reward_tt_dis.append(np.average(bitrwate_reward_tt[i*10:(i+1)*10]))
                bitrate_reward_opt_dis.append(np.average(bitrwate_reward_opt[i*10:(i+1)*10]))


ecdf_tt = ECDF(total_tt)
ecdf_dashlet = ECDF(total_dashlet)
ecdf_opt = ECDF(total_opt)
plt.plot(ecdf_tt.x, ecdf_tt.y, label="TikTok", lw=3)
plt.plot(ecdf_dashlet.x, ecdf_dashlet.y, label="Dashlet", lw=3)
plt.plot(ecdf_opt.x, ecdf_opt.y, label="Oracle", lw=3, linestyle="--")
plt.legend()
plt.grid()
plt.xlim([-1000, 2500])
# plt.show()
plt.ylabel("CDF")
plt.xlabel("Average QoE over every 10 videos")
plt.savefig("qoe-cdf-dashlet-vs-tt.png", bbox_inches='tight')
plt.close()



# only bitrate no rebuffering
ecdf_tt = ECDF(bitrate_reward_tt_dis)
ecdf_dashlet = ECDF(bitrate_reward_dashlet_dis)
ecdf_opt = ECDF(bitrate_reward_opt_dis)
plt.plot(ecdf_tt.x, ecdf_tt.y, label="TikTok", lw=3)
plt.plot(ecdf_dashlet.x, ecdf_dashlet.y, label="Dashlet", lw=3)
plt.plot(ecdf_opt.x, ecdf_opt.y, label="Oracle", lw=3, linestyle="--")
plt.xlim([-1000, 2500])
plt.legend()
plt.grid()
# plt.show()
plt.ylabel("CDF")
plt.xlabel("Average Bitrate award over every 10 videos")
plt.savefig("bitrate-award-cdf-dashlet-vs-tt.png", bbox_inches='tight')
plt.close()



throughput_dashlet_mean = []
throughput_tt_mean = []

x_throughput = []
for i in range(3, 10):
    throughput_dashlet_mean.append(np.average(by_throughput_dashlet[i]))
    throughput_tt_mean.append(np.average(by_throughput_tt[i]))
    x_throughput.append(i)


plt.plot(x_throughput, throughput_tt_mean, label="TikTok", lw=3)
plt.plot(x_throughput, throughput_dashlet_mean, label="Dashlet", lw=3)

plt.legend()
plt.grid()
plt.xlabel("Average network throughput for the trace (Mbps)")
plt.ylabel("Average QoE")
# plt.show()

plt.savefig("qoe-throughput-dashlet-vs-tt.png", bbox_inches='tight')
plt.close()



ecdf_tt = ECDF(rebuffer_tt_dis)
ecdf_dashlet = ECDF(rebuffer_dashlet_dis)

plt.plot(ecdf_tt.x, ecdf_tt.y, label="TikTok", lw=3)
plt.plot(ecdf_dashlet.x, ecdf_dashlet.y, label="Dashlet", lw=3)
plt.legend()
plt.grid()
# plt.show()
plt.ylabel("CDF")
plt.xlabel("Total rebuffering over every 10 videos")
plt.savefig("rebuffer-cdf-dashlet-vs-tt.png", bbox_inches='tight')
plt.close()

throughput_dashlet_mean = []
throughput_tt_mean = []



# def getreward(trace):
#     reward_list = []
#     for i in range(len(trace)):
#         reward = bitraterewards[int(trace[i][1])] - penalty_weight * trace[i][0]
#         reward_list.append(reward)
#
#     return reward_list
#
#
# def process_trace(algorithm_iter, probability_iter, network_traces, viewing_traces):
#     ret = []
#
#     for network_iter in network_traces:
#         for viewing_iter in viewing_traces:
#
#             logpath = f"{args.inputpath}/{algorithm_iter}/{probability_iter}/{network_iter}/{viewing_iter}"
#             trace = np.loadtxt(logpath)
#
#             reward_lists = getreward(trace)
#
#             cur_reward = np.average(reward_lists)
#
#             ret.append(cur_reward)
#
#     return ret
# def main(args):
#
#     cnt = 0
#     algorithm_list = ["empc"]
#     probability_models = ["byvideo"]
#     # network_traces = os.listdir(args.networktraces)[:2]
#     network_traces = ["trace_9284_http---www.msn.com", "trace_10647_http---www.google.com-mobile-", "trace_6420_http---www.ebay.com", "trace_5357_http---www.ebay.com", "trace_5300_http---www.google.com-mobile-", "trace_28652_http---www.youtube.com", "trace_662422_http---edition.cnn.com", "trace_614990_http---www.google.com-mobile-"]
#     viewing_traces = os.listdir(args.viewingtraces)
#
#     svs_trace = process_trace("empc", "byvideo", network_traces, viewing_traces)
#     svs_by_user = process_trace("empc", "byuser", network_traces, viewing_traces)
#     oracle_trace = process_trace("empc", "full_accuracy", network_traces, viewing_traces)
#
#
#
#
#
#
#
#     ecdf_sv = ECDF(svs_trace)
#     ecdf_sv_user = ECDF(svs_by_user)
#     ecdf_oracle = ECDF(oracle_trace)
#
#
#     print("====================")
#     print(np.median(svs_trace) / np.median(oracle_trace))
#     print(np.average(svs_trace) / np.average(oracle_trace))
#
#     print("====================")
#     print(np.median(svs_by_user) / np.median(oracle_trace))
#     print(np.average(svs_by_user) / np.average(oracle_trace))
#
#
#     fig = plt.figure(figsize=(6, 3))
#
#     plt.plot(ecdf_sv.x, ecdf_sv.y, label="SVS byvideo", lw=3)
#     plt.plot(ecdf_sv_user.x, ecdf_sv_user.y, label="SVS byuser", lw=3)
#     plt.plot(ecdf_oracle.x, ecdf_oracle.y, label="Perfect Swipe", lw=3)
#
#
#
#     plt.xlim(0, 10000)
#     plt.ylabel("CDF")
#     plt.xlabel("Average QoE")
#
#     plt.legend()
#     plt.savefig("result2.png", bbox_inches='tight')
#     plt.close()
#
#
#
#
#
#     print(cnt)
#
#     return 0
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--viewingtraces', default='/home/acer/Documents/ttstream/testing/dataclean/data', help='Viewing trace path')
#     parser.add_argument('--networktraces', default='/home/acer/Downloads/pensieve-master/traces/fcc/mahimahi', help='The id to sequence number mapping')
#     parser.add_argument('--inputpath', default='/home/acer/Documents/ttstream/run/cooked-sim', help='The path to save processed data')
#     # parser.add_argument('--inputpath', default='/home/acer/Documents/ttstream/run/result-sim', help='The path to save processed data')
#
#     args = parser.parse_args()
#     main(args)


