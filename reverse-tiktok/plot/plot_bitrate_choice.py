import os
import json
import numpy as np
import argparse
import time
import csv
import xml.etree.ElementTree as ET
import re
import matplotlib.pyplot as plt
from random import sample

plt.rcParams.update({'font.size': 36})
plt.rcParams["font.family"] = "Times New Roman"

folder = "/home/acer/Documents/ttstream/contentServer/dash/data/"

IDX_SEQ = 0
IDX_URI = 1
IDX_BITRATE = 3

class env:

    def _parseTime(self, path):
        tree = ET.parse(path + "/manifest.mpd")

        root = tree.getroot()

        field = root.attrib["mediaPresentationDuration"]
        num_str = re.sub("[^0-9.]", "", field)

        return float(num_str)

    def loadSwipe(self, tracename):
        swipe_percentage = np.loadtxt(tracename)

        nlen = min(len(swipe_percentage), len(self.swipe_trace))

        for i in range(nlen):
            self.swipe_trace[i][1] = self.swipe_trace[i][0] * swipe_percentage[i]

    def loadSequence(self, seqname):
        self.seq_map = {}
        self.swipe_trace = []
        # self.maxbitrate_trace = []
        self.sequence = []

        row_cnt = 0
        with open(seqname, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:


                duration = self._parseTime(folder + row[IDX_URI])

                self.swipe_trace.append([duration, 0, int(row[IDX_SEQ])])

                if row[IDX_URI] not in self.seq_map.keys():
                    self.seq_map[row[IDX_URI]] = len(self.sequence)
                self.sequence.append(row[IDX_URI])

                row_cnt += 1

    def __init__(self, seqname, traceanme):
        self.loadSequence(seqname)
        self.loadSwipe(traceanme)


chunklength = 5.00


def get_all_bitrate(foldername, play_log_name, total_dict):

    with open(foldername+play_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if len(row) > 0:
                if row[1] not in total_dict.keys():
                    bitrates = row[3].split("&")

                    bitrates_val = [int(bitrate) for bitrate in bitrates]
                    bitrates_val = sorted(bitrates_val)
                    total_dict[row[1]] = bitrates_val

def cook_trace(swipetrace, playtrace, logname, total_dict):

    e = env(playtrace, swipetrace)

    fd = open(logname, 'r')
    lines = fd.readlines()

    total_passed_time = 0
    total_download_time = 0

    total_download_size = 0

    buffer_map = {}

    throughput_history = []

    arrx = []
    arry = []
    arrz = []
    for line in lines:
        items = line.split()

        throughput = float(items[7]) * 8 / 1000 / (float(items[5]) - float(items[4]))

        throughput_history.append(throughput)

        if items[1] in total_dict.keys():
            bitrates = total_dict[items[1]]

            if len(throughput_history) > 1:

                arrx.append(throughput_history[-1])
                # bitrates = total_dict[entry[3]]
                arry.append(bitrates[-1] / 1000000)
                arrz.append(bitrates[int(items[3])] / bitrates[-1])



    return arrx, arry, arrz

network_tp_list = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0]
# network_tp_list = [17.5]

def main(args):

    # ufd = open(f"{args.dumppath}usage.txt", "w")

    # for network_idx in range(6, 20):
    #     network_tp = network_idx / 2.0

    total_dict = {}

    arrx = []
    arry = []
    arrc = []

    for netid in range(6, 41):
        for swipeid in range(2, 5):

            foldername = f"/home/acer/Documents/reverse-tiktok/data/trace-{netid / 2:.1f}-swipe-{swipeid}/"
            play_log_name = f"trace-{netid / 2:.1f}-swipe-{swipeid}-play.csv"

            get_all_bitrate(foldername, play_log_name, total_dict)

    for network_tp in network_tp_list:

        for swipe_idx in range(2, 6):

            testname = f"trace-{network_tp:.1f}-swipe-{swipe_idx}"

            network_tp2 = network_tp

            # if network_tp2 > 9.5:
            #     network_tp2 = (int(network_tp2 * 2) % 4) / 2 + 8

            testname2 = f"trace-{network_tp2:.1f}-swipe-{swipe_idx}"

            playtracepath = f"/home/acer/Documents/reverse-tiktok/data/{testname2}/{testname2}-play.csv"

            # playtracepath = f"/home/acer/Documents/reverse-tiktok/data/{testname}/{testname}-play.csv"

            swipetracepath = f"/home/acer/Documents/reverse-tiktok/traces/swipe/swipe-{swipe_idx}.txt"

            loginname = f"{args.inputpath}{testname}.txt"
            # logoutname = f"{args.dumppath}{testname}.txt"

            print(loginname)
            arrxf, arryf, arrzf = cook_trace(swipetracepath, playtracepath, loginname, total_dict)

            arrx.extend(arrxf)
            arry.extend(arryf)
            arrc.extend(arrzf)

    data_dict = [{} for i in range(26)]
    for i in range(len(arrx)):

        tp = min(25, int(arrx[i]))

        bitrate_max = int(arry[i] * 10)

        if bitrate_max not in data_dict[tp].keys():
            data_dict[tp][bitrate_max] = []

        data_dict[tp][bitrate_max].append(arrc[i])

    fd = open("bitrate_table.log", "w")

    for i in range(26):

        for bitrate_max in data_dict[i].keys():
            fd.write(f"{i} {bitrate_max} {np.average(data_dict[i][bitrate_max])}\n")



    fd.close()

    idx = [i for i in range(len(arrx))]
    # idx_s = sample(idx, 20000)
    idx_s = idx
    arrx = [arrx[i] / 0.8 for i in idx_s]
    arry = [arry[i] for i in idx_s]
    arrc = [arrc[i] for i in idx_s]


    cmap = plt.get_cmap('rainbow')
    cmaplist = [cmap(i) for i in arrc]

    tmp = 1
    # print(slope)
    # slope = 93874.02577906292
    # print(intercept)
    # intercept = 150858.48070105485

    # plt.gca().invert_yaxis()
    #
    # plt.xlabel("Throughput (Mbps)")
    # plt.ylabel("# of buffered video")
    # plt.xticks([0, 1, 2, 3, 4, 5, 6, 7], [2, 4, 6, 8, 10, 12, 14, 16])
    # plt.yticks([0, 1, 2, 3, 4], ["rebuffer", "1", "2", "3", "4"], rotation=90)
    # bar = plt.colorbar(ax)
    # bar.ax.set_yticks([400, 450, 500, 550, 600, 650, 700, 750])
    # bar.ax.set_yticklabels(["400   ", "450   ", "500   ", "550   ", "600   ", "650   ", "700   ", "750   "])

    plt.figure(figsize=(10, 10))


    # plt.plot([0, 20], [intercept, 20 * slope + intercept], "r")
    plt.scatter(arrx, arry, c=cmaplist)
    plt.xlim([0, 25])

    # plt.imshow([[0, 1], [0, 1]], cmap=cmap)
    # cbar = plt.colorbar()
    # cbar.ax.set_ylabel("chosen bitrate / highest bitrate")

    plt.ylabel("Highest possible bitrate (Mbps)")
    plt.xlabel("Download Throughput (Mbps)")

    # fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)

    plt.savefig("bitrate_choice_dashlet.png")
    plt.close()

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputpath', default='/home/acer/Documents/ttstream/run/result-sim/dashlet/', help='The path to get processed data')

    args = parser.parse_args()
    main(args)



# import csv
# import numpy as np
# import matplotlib.pyplot as plt
# import random
# from statsmodels.distributions.empirical_distribution import ECDF
# import scipy.stats as st
#
# plt.rcParams.update({'font.size': 36})
# plt.rcParams["font.family"] = "Times New Roman"
# def get_download_range(range_str):
#     range_items = range_str.split()
#
#     if len(range_items) == 1:
#         return (0, 0)
#
#     range_entries = range_items[1].split("/")
#
#     range_values = range_entries[0].split("-")
#
#
#     return (int(range_values[0]), int(range_values[1]))
#
#
# IDX_DOWNLOAD_URI = 7
# IDX_DOWNLOAD_RANGE = 1
#
# IDX_REQUEST_START = 2
# IDX_REQUEST_END = 3
#
# IDX_RESPONSE_START = 4
# IDX_RESPONSE_END = 5
#
#
#
# def get_all_bitrate(foldername, play_log_name, total_dict):
#
#     with open(foldername+play_log_name, newline='') as csvfile:
#         spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#         for row in spamreader:
#             if len(row) > 0:
#                 if row[1] not in total_dict.keys():
#                     bitrates = row[3].split("&")
#
#                     bitrates_val = [int(bitrate) for bitrate in bitrates]
#                     bitrates_val = sorted(bitrates_val)
#                     total_dict[row[1]] = bitrates_val
#
#
#                     tmp = 1
#             # total_dict
#
#
#
# def analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name):
#
#     play_log = []
#     download_log = []
#     swipe_log = [0]
#
#
#     uri_dict = {}
#     uri_real_dict = {}
#
#
#     with open(foldername+swipe_log_name, newline='') as csvfile:
#         spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#         for row in spamreader:
#             swipe_log.append(float(row[1]) - 0.1)
#
#
#
#     with open(foldername+play_log_name, newline='') as csvfile:
#         spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#         for row in spamreader:
#             bitrates = row[3].split("&")
#
#             encode_uri = row[4].split("&")
#
#             bitrates_val = [int(bitrate) for bitrate in bitrates]
#
#             # bitrates_val = sorted(bitrates_val)
#
#             parsed_row = [int(row[0]), row[1], int(row[2]), bitrates_val, encode_uri, row[5]]
#
#
#             for i in range(len(encode_uri)):
#                 uri_dict[encode_uri[i]] = (int(row[0]), int(i/2), len(bitrates))
#                 uri_real_dict[encode_uri[i]] = row[1]
#
#             play_log.append(parsed_row)
#
#     play_idx = 0
#
#
#     max_download_chunk = 0
#
#     download_progress = [(0, 0) for i in range(len(play_log))]
#
#     throughput_all = []
#
#
#     bitrate_buffer_list = []
#
#     with open(foldername+download_log_name, newline='') as csvfile:
#         spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#         for row in spamreader:
#             download_log.append(row)
#
#             for i in range(len(row)):
#                 row[i] = row[i].strip()
#
#             if row[IDX_DOWNLOAD_URI] in uri_dict.keys():
#                 ranges = get_download_range(row[IDX_DOWNLOAD_RANGE])
#
#                 download_metadata = uri_dict[row[IDX_DOWNLOAD_URI]]
#                 downloadIdx = download_metadata[0]
#                 bitrateIdx = download_metadata[1]
#
#                 bitrate_decision = play_log[downloadIdx][3][bitrateIdx]
#
#
#
#                 bitrate_combo = (bitrate_decision, download_metadata[1], download_metadata[2] - 1)
#
#
#                 if ranges[0] != 1024000 and ranges[1] - ranges[0] != 0:
#                     request_start_time = float(row[IDX_REQUEST_START])
#
#                     while (play_idx + 1 < len(swipe_log) and swipe_log[play_idx + 1] < request_start_time):
#                         play_idx += 1
#
#
#                     if len(throughput_all) > 1:
#                         print(len(throughput_all))
#                         bitrate_buffer_list.append([bitrate_combo, downloadIdx - play_idx - 1, throughput_all[-1], uri_real_dict[row[IDX_DOWNLOAD_URI]]])
#
#                 if ranges[1] - ranges[0] != 0:
#
#                     this_size = (ranges[1] - ranges[0]) * 8
#
#                     this_time = (float(row[IDX_RESPONSE_END]) - float(row[IDX_RESPONSE_START]))
#
#                     this_throughput = this_size / 1000 / 1000 / this_time
#
#                     # print(this_throughput)
#
#                     throughput_all.append(this_throughput)
#                 else:
#                     tmp = 1
#
#
#     return bitrate_buffer_list
#
#
# bitrate_buffer_all = []
#
# total_dict = {}
#
# for netid in range(6, 41):
#     for swipeid in range(2, 5):
#         foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
#         play_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-play.csv"
#         download_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-download.csv"
#         swipe_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-swipe.log"
#
#         bitrate_buffer_list = get_all_bitrate(foldername, play_log_name, total_dict)
#
#
#
# for netid in range(6, 41):
#     for swipeid in range(2, 6):
#         foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
#         play_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-play.csv"
#         download_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-download.csv"
#         swipe_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-swipe.log"
#
#         print(foldername)
#
#         bitrate_buffer_list = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name)
#
#         bitrate_buffer_all.extend(bitrate_buffer_list)
#
#
# buffers_bitrate_absolute = [[[] for i in range(8)] for j in range(5)]
# buffers_bitrate_relative = [[[] for i in range(8)] for j in range(5)]
#
#
# arrx = []
# arry = []
#
# arrc = []
#
# for entry in bitrate_buffer_all:
#
#     # if (entry[0][1] != 0 and entry[0][1] != entry[0][2]):
#     # if (entry[0][1] == 0):
#
#
#
#     arrx.append(entry[2])
#     bitrates = total_dict[entry[3]]
#     arry.append(bitrates[-1] / 1000000)
#
#     # print(bitrates[entry[0][1]], entry[0][0])
#     arrc.append(entry[0][0] / bitrates[-1])
#
#     # bufferidx = entry[1]
# # slope, intercept, _, _, _ = st.linregress(arrx, arry)
#
# cmap = plt.get_cmap('rainbow')
# cmaplist = [cmap(i) for i in arrc]
#
#
#
# tmp = 1
# # print(slope)
# # slope = 93874.02577906292
# # print(intercept)
# # intercept = 150858.48070105485
#
#
# # plt.gca().invert_yaxis()
# #
# # plt.xlabel("Throughput (Mbps)")
# # plt.ylabel("# of buffered video")
# # plt.xticks([0, 1, 2, 3, 4, 5, 6, 7], [2, 4, 6, 8, 10, 12, 14, 16])
# # plt.yticks([0, 1, 2, 3, 4], ["rebuffer", "1", "2", "3", "4"], rotation=90)
# # bar = plt.colorbar(ax)
# # bar.ax.set_yticks([400, 450, 500, 550, 600, 650, 700, 750])
# # bar.ax.set_yticklabels(["400   ", "450   ", "500   ", "550   ", "600   ", "650   ", "700   ", "750   "])
#
#
#
#
# plt.figure(figsize=(10, 10))
#
# # plt.plot([0, 20], [intercept, 20 * slope + intercept], "r")
# plt.scatter(arrx, arry, c=cmaplist)
# plt.xlim([0, 25])
#
# # plt.imshow([[0, 1], [0, 1]], cmap=cmap)
# # cbar = plt.colorbar()
# # cbar.ax.set_ylabel("Chosen bitrate / Highest bitrate")
#
# plt.ylabel("Highest possible bitrate (Mbps)")
# plt.xlabel("Download Throughput (Mbps)")
#
# # fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
#
# plt.savefig("bitrate_choice.png")
# plt.close()
#
#
# # x = [i / 100 for i in range(101)]
# #
# # cmaplist = [cmap(i) for i in x]
# #
# # plt.figure()
# # plt.scatter(x, x, c=cmaplist)
# #
# # plt.show()
# # plt.close()
#
