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

name_to_length = {}

# 102.7
trace_start_offset = 97.3

random.seed(0)
def quality_to_color(quality):
    quality_to_idx = {"adapt_lower_720" : 3, "adapt_lower_720_1": 3, "adapt_540_1": 2, "lower_540": 1, "lower_540_1": 1, "lowest_540_1": 0, "lowest_540": 0, "normal_360_0": 1, "normal_360": 1, "normal_480_0": 2, "normal_480": 2, "normal_540_0": 0, "normal_540_1": 2, "": 0, "adapt_lowest_360_1": 0, "lowest_540_0": 0, "lower_540_0": 0}

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


def get_swipe_log(swipe_log_name):
    IDX_START_TIME = 0
    IDX_START_X = 1
    IDX_START_Y = 2
    IDX_END_TIME = 3
    IDX_END_X = 4
    IDX_END_Y = 5

    data = np.loadtxt(swipe_log_name)

    # while abs(data[0][IDX_START_X] - 679) >= 100 or abs(data[0][IDX_START_Y] - 1486) >= 100:
    #     data = data[1:]
    #     tmp = 1

    start_time = data[0][IDX_START_TIME]

    event_list = []

    for entry in data:

        if abs(entry[IDX_START_Y] - entry[IDX_END_Y]) > abs(entry[IDX_END_X] - entry[IDX_START_X]):
            if abs(entry[IDX_START_Y] - entry[IDX_END_Y]) > 100:
                if entry[IDX_START_Y] - entry[IDX_END_Y] > 0:
                    event_list.append(("up", entry[IDX_END_TIME]))
                else:
                    event_list.append(("down", entry[IDX_END_TIME]))
        else:
            if abs(entry[IDX_END_X] - entry[IDX_START_X]) > 100:
                if entry[IDX_END_X] - entry[IDX_START_X] > 0:
                    event_list.append(("right", entry[IDX_END_TIME]))
                else:
                    event_list.append(("left", entry[IDX_END_TIME]))
    # print((data[0][0], data[0][1], data[0][2], data[0][3], data[0][4], data[0][5]))

    return event_list, start_time

def calibrate_swipe_clock(event_list_t, app_start_time_t, download_request_list_p, start_time_p):
    idx = 0

    start_time_p -= 2

    event_list = []

    while idx < len(event_list_t):
        if event_list_t[idx][0] == "up":
            event_list.append(event_list_t[idx][1])

        elif event_list_t[idx][0] == "down":
            idx += 2
            continue

        idx += 1

    sorted(download_request_list_p)

    for i in range(len(download_request_list_p)):
        download_request_list_p[i] -= start_time_p

    for i in range(len(event_list)):
        event_list[i] -= app_start_time_t

    delta_time = 0

    max_reward = 0
    max_delta_time = 0

    reward_history = []
    delta_history = []

    while delta_time < 3:
        event_list_test = []

        for i in range(len(event_list)):
            event_list_test.append(event_list[i] + delta_time)

        this_reward = 0

        point_i = 0
        point_j = 0

        while (point_i < len(event_list_test) and point_j < len(download_request_list_p)):

            if event_list_test[point_i] > download_request_list_p[point_j]:
                point_j += 1
            elif event_list_test[point_i] + 1> download_request_list_p[point_j]:

                this_reward += 1
                point_i += 1
                point_j += 1
            else:
                point_i += 1

        if this_reward > max_reward:
            max_reward = this_reward
            max_delta_time = delta_time

        reward_history.append(this_reward)
        delta_history.append(delta_time)
        delta_time += 0.5

    for i in range(len(event_list)):
        event_list[i] += max_delta_time

    point_i = 0
    point_j = 0

    fine_tune_list = []

    while (point_i < len(event_list) and point_j < len(download_request_list_p)):

        if event_list[point_i] > download_request_list_p[point_j]:
            point_j += 1
        elif event_list[point_i] + 1 > download_request_list_p[point_j]:
            # print(point_i)

            fine_tune_list.append(download_request_list_p[point_j] - event_list[point_i])

            point_i += 1
            point_j += 1
        else:
            point_i += 1

    additional_offset = np.median(fine_tune_list)

    for i in range(len(event_list)):
        event_list[i] += start_time_p + additional_offset
    return event_list


def analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name, start_time_name):

    play_log = []
    download_log = []

    uri_dict = {}

    uri_to_quality = {}
    uri_to_bitrate = {}
    uri_to_bitrate_list = {}
    uri_to_vname = {}

    event_list, app_start_time_t = get_swipe_log(foldername+swipe_log_name)

    vidx_to_vname = {}
    vidx_visited = {}

    with open(foldername+play_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')



        for row in spamreader:
            if len(row) < 12:
                play_log.append([])
                continue

            bitrates = row[3].split("&")

            encode_uri = row[4].split("&")

            quality_string = row[6].split("&")

            parsed_row = [int(row[0]), row[1], int(row[2]), [int(bitrate) for bitrate in bitrates], encode_uri, row[5]]

            vidx_to_vname[int(row[0])] = row[1]
            vidx_visited[int(row[0])] = False

            name_to_length[row[1]] = float(row[2]) / 1000


            for i in range(len(encode_uri)):

                uri_dict[encode_uri[i]] = (int(row[0]), int(i/2), len(bitrates))
                uri_to_quality[encode_uri[i]] = quality_string[int(i/2)]
                uri_to_bitrate[encode_uri[i]] = int(bitrates[int(i/2)])
                uri_to_bitrate_list[encode_uri[i]] = [int(bitrates[j]) for j in range(len(bitrates))]
                uri_to_vname[encode_uri[i]] = row[1]

            play_log.append(parsed_row)

    first_entries = []
    second_entries = []

    request_start_time_list = []

    with open(foldername+download_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:

            if len(row) < 9:
                continue

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

                video_duration = play_log[downloadIdx][2]

                chunk_duration = size_in_bytes / total_size_in_bytes * play_log[downloadIdx][2]

                request_start_time_list.append(float(row[IDX_REQUEST_START]))

                # print(ranges[0])
                # IDX_REQUEST_START
                if ranges[0] != 1024001:
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
                        bitrate_decision,
                        uri_to_vname[row[IDX_DOWNLOAD_URI]],
                        video_duration
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
                        bitrate_decision,
                        uri_to_vname[row[IDX_DOWNLOAD_URI]],
                        video_duration
                    ])

    # print(first_entries[0][4] - app_start_time_t)

    data_start_time_name = 0

    with open(foldername+start_time_name) as fd:
        sline = fd.readline()
        data_start_time_name = float(sline.strip())

    swipe_log = [0]

    swipe_clock = calibrate_swipe_clock(event_list, app_start_time_t, request_start_time_list, data_start_time_name)

    np.savetxt(foldername+swipe_log_name+"xyz", swipe_clock, fmt="%10.5f")

    swipe_clock = np.loadtxt(foldername+swipe_log_name+"xyz")
    for i in range(len(swipe_clock)):
        swipe_log.append(swipe_clock[i])

    return swipe_log, first_entries, second_entries



def gen_distribution_template(ratio_all):
    distribution = [0] * 1001

    for i in range(len(ratio_all)):
        distribution[min(round(ratio_all[i] * 1000), 1000)] += 1

    for i in range(1001):
        distribution[i] /= len(ratio_all)

    return distribution

def convert_swipe_distribution(distribution, duration):
    arr = [0] * (int(duration - 0.00000000001) + 1)
    nlen = len(arr)

    for i in range(len(distribution)):

        idx = min(int(0.001 * i * duration), nlen-1)

        arr[idx] += distribution[i]



    for i in range(len(arr)):
        arr[i] = arr[i] * 0.9 + 0.1 / len(arr)


    return arr



bitrate_throughput_all = []

bitrate_buffer_all = []

tmp = 1

ratio_all = []

ratio_short = []
ratio_long = []

ratio_mid = []



for userid in range(101, 111):
    for networkstr in ["low", "mid", "high"]:
        foldername = f"../data/tt-{userid}-{networkstr}/"
        play_log_name = f"tt-{userid}-{networkstr}-play.csv"
        download_log_name = f"tt-{userid}-{networkstr}-download.csv"
        swipe_log_name = f"tt-{userid}-{networkstr}-swipe-time.log"
        start_time_name = f"tt-{userid}-{networkstr}-downloadstart.log"

        print(foldername)

        swipe_log, first_entries, _ = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name, start_time_name)

        first_entries_parsed = {}

        for entry in first_entries:
            first_entries_parsed[entry[2]] = [entry[0], entry[1], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9], entry[10], entry[12]]

            if entry[-2] not in name_to_length.keys():
                name_to_length[entry[-2]] = entry[-1] / 1000

        watch_time = []
        total_time = []

        time_pair = []
        for i in range(1, len(swipe_log)-1):
            if i not in first_entries_parsed.keys():
                continue

            watch_time.append(swipe_log[i+1] - swipe_log[i])

            total_time.append(first_entries_parsed[i][-1] / 1000)

            time_pair.append((swipe_log[i+1] - swipe_log[i], first_entries_parsed[i][-1] / 1000))

            swipe_percent = (swipe_log[i + 1] - swipe_log[i]) / (first_entries_parsed[i][-1] / 1000)

            ratio_all.append(swipe_percent)

            if first_entries_parsed[i][-1] / 1000 < 15:
                ratio_short.append(swipe_percent)

            elif first_entries_parsed[i][-1] / 1000 > 60:
                ratio_long.append(swipe_percent)

            else:
                ratio_mid.append(swipe_percent)


distribution_short = gen_distribution_template(ratio_short)
distribution_long = gen_distribution_template(ratio_long)
distribution_mid = gen_distribution_template(ratio_mid)


print(np.sum(distribution_short))
print(np.sum(distribution_mid))
print(np.sum(distribution_long))

for name_key in name_to_length.keys():
    duration = name_to_length[name_key]

    result = []

    if duration < 15:
        result = convert_swipe_distribution(distribution_short, duration)
    elif duration > 60:
        result = convert_swipe_distribution(distribution_long, duration)
    else:
        result = convert_swipe_distribution(distribution_mid, duration)


    fd = open(f"/home/acer/Documents/ttstream/abr_server/probability/user-study/{name_key}.txt", "w")

    for i in range(len(result)):
        fd.write(f"{result[i]:1.10f}\n")
    fd.close()
    # print(result)



