import csv
import os.path

import numpy as np
import matplotlib.pyplot as plt
import random
from statsmodels.distributions.empirical_distribution import ECDF
from matplotlib.patches import Rectangle

plt.rcParams.update({'font.size': 25})

cmap = plt.get_cmap('rainbow')
cmaplist = [cmap(i) for i in range(cmap.N)]

cmaplist2 = [
    (75/255.0, 0/255.0, 130/255.0),
    (0/255.0, 0/255.0, 255/255.0),
    (0/255.0, 255/255.0, 0/255.0),
    (225/255.0, 225/255.0, 0/255.0),
    (255/255.0, 127/255.0, 0/255.0),
    (255/255.0, 0/255.0, 0/255.0),
]

cmaplist = cmaplist[168:]

cmaplist = ["b", "g", (1.0, 0.5, 0), "r"]

# 102.7
trace_start_offset = 97.3

random.seed(0)
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
    uri_to_bitrate = {}
    uri_to_bitrate_list = {}



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
                uri_to_bitrate[encode_uri[i]] = int(bitrates[int(i/2)])
                uri_to_bitrate_list[encode_uri[i]] = [int(bitrates[j]) for j in range(len(bitrates))]

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

                size_in_bytes = ranges[1] - ranges[0]

                total_size_in_bytes = int(play_log[downloadIdx][2] * uri_to_bitrate[row[IDX_DOWNLOAD_URI]] / 1000 / 8)


                if size_in_bytes == 0:
                    size_in_bytes = total_size_in_bytes

                # if ranges[0] == 1024000:
                #     size_in_bytes = size_in_bytes + 100000 * ((downloadIdx%6) / 6)
                throughput_est = size_in_bytes * 8 / 1000 / 1000 / (float(row[IDX_RESPONSE_END]) - float(row[IDX_RESPONSE_START]))

                chunk_duration = size_in_bytes / total_size_in_bytes * play_log[downloadIdx][2]

                # IDX_REQUEST_START
                if ranges[0] != 1024000:
                    first_entries.append([
                        float(row[IDX_RESPONSE_START]),
                        float(row[IDX_RESPONSE_END]),
                        downloadIdx,
                        uri_to_quality[row[IDX_DOWNLOAD_URI]],
                        float(row[IDX_REQUEST_START]),
                        throughput_est,
                        size_in_bytes,
                        total_size_in_bytes,
                        chunk_duration,
                        uri_to_bitrate_list[row[IDX_DOWNLOAD_URI]],
                        bitrate_decision
                    ])
                else:
                    second_entries.append([
                        float(row[IDX_RESPONSE_START]),
                        float(row[IDX_RESPONSE_END]),
                        downloadIdx,
                        uri_to_quality[row[IDX_DOWNLOAD_URI]],
                        float(row[IDX_REQUEST_START]),
                        throughput_est,
                        size_in_bytes,
                        total_size_in_bytes,
                        chunk_duration,
                        uri_to_bitrate_list[row[IDX_DOWNLOAD_URI]],
                        bitrate_decision
                    ])

    return swipe_log, first_entries, second_entries




def draw_bar(ax, i, start, end, barcolor, second_half):
    if second_half == False:
        ax.add_patch(Rectangle((start, i), end-start, 1, color=barcolor))
    else:
        ax.add_patch(Rectangle((start, i), end-start, 1, facecolor=barcolor, hatch='x', edgecolor='k'))


def draw_rebuffer(ax, start, end):
    ax.add_patch(Rectangle((start, 0), end-start, 1000000000000, color=(181/255, 181/255, 181/255), zorder=1))

def draw_ramp(ax, start, end):
    ax.add_patch(Rectangle((start, 0), end-start, 1000000000000, color=(0.96, 0.8, 0.8), zorder=0))

def draw_maintain(ax, start, end):
    ax.add_patch(Rectangle((start, 0), end-start, 1000000000000, color=(0.85, 0.92, 0.83), zorder=0))

def draw_idle(ax, start, end):
    ax.add_patch(Rectangle((start, 0), end-start, 1000000000000, color=(0.79, 0.85, 0.97), zorder=0))

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


ramp_up_dist = []
buffer_maintain_dist = []
idle_dist = []



rebuffer_due_to_idle = 0 #
rebuffer_due_to_download_second_half = 0
rebuffer_due_to_download_first_half = 0

rebuffer_due_to_premature_binding = 0

rebuffer_due_to_previous_rebuffer = 0 #
rebuffer_all = 0


def judge_idle(slots, idx):

    look_back = max(0, idx - 2000)

    idle_cnt = 0
    for i in range(look_back, idx):
        if slots[i] == 0:
            idle_cnt += 1

    if idle_cnt / (idx - look_back) > 0.25:
        return True

    return False







for netid in range(6, 20):
    for swipeid in range(2, 6):

        net_data = load_network(f"../traces/network/trace-{netid/2:.1f}.down")
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

        download_slots = [0] * 100000

        last_rebuffer_time = -10000
        last_download_type = "first"



        rebuffer_gap = 5

        for i in range(len(swipe_log)):
            swipe_log[i] -= bias

        for entry in first_entries:
            first_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]

        for entry in second_entries:
            second_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]

        d_len = first_entries[-1][2] + 1


        for i in range(1, len(swipe_log) - 1):

            if i in first_entries_parsed.keys():

                if swipe_log[i] < first_entries_parsed[i][1]:
                    # draw_rebuffer(ax, min(first_entries_parsed[i][1], swipe_log[i+1]), swipe_log[i])

                    if swipe_log[i] > last_rebuffer_time + 5:
                        if judge_idle(download_slots, int(swipe_log[i] * 100)):
                            rebuffer_due_to_idle += 1

                    else:
                        rebuffer_due_to_previous_rebuffer += 1

                    rebuffer_all += 1
                    last_rebuffer_time = min(first_entries_parsed[i][1], swipe_log[i+1])

                play_start_time = max(first_entries_parsed[i][1], swipe_log[i])
                second_entries_start = play_start_time + first_entries_parsed[i][7] / 1000

                if second_entries_start < swipe_log[i+1]:
                    if i in second_entries_parsed.keys():
                        rebuffer_finish = min(swipe_log[i+1], second_entries_parsed[i][1])

                        if rebuffer_finish > second_entries_start:
                            if rebuffer_finish - second_entries_start > 0.5:

                                if second_entries_start > last_rebuffer_time + 5:

                                    if judge_idle(download_slots, int(second_entries_start * 100)):
                                        rebuffer_due_to_idle += 1

                                else:
                                    rebuffer_due_to_previous_rebuffer += 1

                                last_rebuffer_time = rebuffer_finish
                                rebuffer_all += 1
                    else:
                        if swipe_log[i+1] - second_entries_start > 0.5:

                            if second_entries_start > last_rebuffer_time + 5:
                                if judge_idle(download_slots, int(second_entries_start * 100)):
                                    rebuffer_due_to_idle += 1
                            else:
                                rebuffer_due_to_previous_rebuffer += 1

                            rebuffer_all += 1
                            last_rebuffer_time = swipe_log[i+1]

                s_idx = int(first_entries_parsed[i][0] * 100)
                e_idx = int(first_entries_parsed[i][1] * 100)

                for t_idx in range(s_idx, e_idx):
                    download_slots[t_idx] = 1

