import csv
import os.path

import numpy as np
import matplotlib.pyplot as plt
import random
from statsmodels.distributions.empirical_distribution import ECDF
from matplotlib.patches import Rectangle

plt.rcParams.update({'font.size': 18})


cmap = plt.get_cmap('rainbow')
cmaplist = [cmap(i) for i in range(cmap.N)]

cmaplist = cmaplist[168:]

cmaplist = ["b", "g", (1.0, 0.5, 0), "r"]

# 102.7
trace_start_offset = 97.3


def quality_to_color(quality):
    quality_to_idx = {"adapt_lower_720_1": 3, "adapt_540_1": 2, "lower_540_1": 1, "lowest_540_1": 0, "normal_480_0": 2, "normal_540_1": 2, "lowest_540_0": 0, "lower_540_0": 0}

    idx = int(quality_to_idx[quality] * (len(cmaplist) - 1) / 3)

    return cmaplist[idx]


def get_download_range(range_str):
    range_items = range_str.split()

    if len(range_items) == 1:
        return (0, 0)

    range_entries = range_items[1].split("/")

    range_values = range_entries[0].split("-")


    return (int(range_values[0]), int(range_values[1]))


IDX_DOWNLOAD_URI = 7
IDX_DOWNLOAD_RANGE = 1

IDX_REQUEST_START = 2
IDX_REQUEST_END = 3

IDX_RESPONSE_START = 4
IDX_RESPONSE_END = 5


def analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name):

    play_log = []
    download_log = []
    swipe_log = [0]


    uri_dict = {}

    uri_to_quality = {}



    with open(foldername+swipe_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            swipe_log.append(float(row[1]))


    with open(foldername+play_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            bitrates = row[3].split("&")

            encode_uri = row[4].split("&")

            quality_string = row[6].split("&")

            parsed_row = [int(row[0]), row[1], int(row[2]), [int(bitrate) for bitrate in bitrates], encode_uri, row[5]]


            for i in range(len(encode_uri)):
                uri_dict[encode_uri[i]] = (int(row[0]), int(i/2), len(bitrates))
                uri_to_quality[encode_uri[i]] = quality_string[int(i/2)]

            play_log.append(parsed_row)
            # print(', '.join(row))


    # print(uri_dict.keys())



    play_idx = 0


    max_download_chunk = 0

    download_progress = [(0, 0) for i in range(len(play_log))]

    throughput_all = []


    first_entries = []
    second_entries = []


    with open(foldername+download_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            download_log.append(row)

            for i in range(len(row)):
                row[i] = row[i].strip()

            if row[IDX_DOWNLOAD_URI] in uri_dict.keys():
                ranges = get_download_range(row[IDX_DOWNLOAD_RANGE])

                download_metadata = uri_dict[row[IDX_DOWNLOAD_URI]]
                downloadIdx = download_metadata[0]
                bitrateIdx = download_metadata[1]

                bitrate_decision = play_log[downloadIdx][3][bitrateIdx]

                bitrate_combo = (bitrate_decision, download_metadata[1], download_metadata[2] - 1)

                throughput_est = (ranges[1] - ranges[0]) * 8 / 1000 / 1000 / (float(row[IDX_RESPONSE_END]) - float(row[IDX_RESPONSE_START]))

                # IDX_REQUEST_START
                if ranges[0] != 1024000:
                    first_entries.append([float(row[IDX_RESPONSE_START]), float(row[IDX_RESPONSE_END]), downloadIdx, uri_to_quality[row[IDX_DOWNLOAD_URI]], float(row[IDX_REQUEST_START]), throughput_est])
                else:
                    second_entries.append([float(row[IDX_RESPONSE_START]), float(row[IDX_RESPONSE_END]), downloadIdx, uri_to_quality[row[IDX_DOWNLOAD_URI]], float(row[IDX_REQUEST_START]), throughput_est])

    return swipe_log, first_entries, second_entries




def draw_bar(ax, i, start, end, barcolor):
    ax.add_patch(Rectangle((start, i), end-start, 1, color=barcolor))


def draw_rebuffer(ax, start, end):
    ax.add_patch(Rectangle((start, 0), end-start, 100, color=(181/255, 181/255, 181/255)))

# def draw_second(ax, i, start, end):
#     ax.add_patch(Rectangle((start, i), end-start, 1, color='b'))

def load_network(filename):
    data = np.loadtxt(filename)

    ret = [0] * int(data[-1] / 1000 + 1)

    for i in range(len(data)):
        ret[int(data[i]/1000)] += 1

    for i in range(len(ret)):

        ret[i] = ret[i] * 1500 * 8 / 1000 / 1000

    return ret

bitrate_throughput_all = []

bitrate_buffer_all = []

buffer_second_time = []


vcnt = 0
for netid in range(7, 20):
    for swipeid in range(2, 7):

        # net_data = load_network(f"../traces/network/trace-{netid/2:.1f}.down")
        foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
        play_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-play.csv"
        download_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-download.csv"
        swipe_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-swipe.log"
        start_time_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-start-time.log"



        print(foldername)



        swipe_log, first_entries, second_entries = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name)

        if len(first_entries) < 10:
            continue

        if os.path.exists(foldername + start_time_name):
            start_time = np.loadtxt(foldername + start_time_name)

            print(swipe_log[1] - start_time)

        bias = first_entries[0][4]

        trace_start_time = swipe_log[1] - trace_start_offset - bias

        first_entries_parsed = {}
        second_entries_parsed = {}


        yaxis = []

        for i in range(len(swipe_log)):
            swipe_log[i] -= bias
            tmp = 1
            yaxis.append(i + 0.5)

        for entry in first_entries:

            first_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5]]

        for entry in second_entries:
            second_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5]]

            # if entry[2]+1 < len(swipe_log):
                # if swipe_log[entry[2]+1] < second_entries_parsed[entry[2]][1]:
                #     second_entries_parsed[entry[2]][1] = swipe_log[entry[2]+1]

        d_len = first_entries[-1][2] + 1

        for i in range(d_len):

            if i in first_entries_parsed.keys():
                vcnt += 1

            if i in second_entries_parsed.keys():
                if i + 1 < len(swipe_log) and second_entries_parsed[i][3] < swipe_log[i + 1]:
                    buffer_second_time.append(second_entries_parsed[i][3] - swipe_log[i] + 0.06214594841003418)

from statsmodels.distributions.empirical_distribution import ECDF


buffer_second_time.sort()

buffer_second_time = buffer_second_time[2:len(buffer_second_time)-4]

print(np.min(buffer_second_time))

np.savetxt("time_diff.txt", buffer_second_time)

print(len(buffer_second_time))
print(vcnt)

ecdf = ECDF(buffer_second_time)
# plt.hist(buffer_second_time, bins=50)
plt.figure(figsize=(8, 4))
plt.plot(ecdf.x, ecdf.y, lineWidth=3)
plt.plot([0, 2.5], [1, 1], "k--")
plt.ylim([0, 1.05])
plt.xlim([0, 2.5])
plt.xlabel("Time (s)")
plt.ylabel("CDF")
plt.title("Time diff. between play and 2nd download start")
plt.grid()
plt.savefig("second_down_start.png", bbox_inches="tight")
plt.close()








