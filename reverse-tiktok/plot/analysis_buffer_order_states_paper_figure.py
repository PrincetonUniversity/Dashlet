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

cmaplist = ["b", "g", (1.0, 0.5, 0), (0.75, 0, 0.75)]

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
    ax.add_patch(Rectangle((start, -2), end-start, 10, color=(0.96, 0.8, 0.8), zorder=0))

def draw_maintain(ax, start, end):
    ax.add_patch(Rectangle((start, -2), end-start, 10, color=(0.85, 0.92, 0.83), zorder=0))

def draw_idle(ax, start, end):
    ax.add_patch(Rectangle((start, -2), end-start, 10, color=(0.79, 0.85, 0.97), zorder=0))

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


buffer_arr = [0] * 1201

for netid in range(10, 11):
    for swipeid in range(2, 3):

        plot_range_low = 30
        plot_range_high = 51

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
            first_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]

        for entry in second_entries:
            second_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]

        first_entries_parsed[39][2] = "adapt_lower_720_1"
        second_entries_parsed[39][2] = "adapt_lower_720_1"

        d_len = first_entries[-1][2] + 1

        # plt.figure(figsize=(30, 4))

        fig, axs = plt.subplots(1, 1, figsize=(30, 5))
        plt.subplots_adjust(hspace=0.3)

        scatter_x = []
        scatter_y = []

        buffer_traces = []

        x_start = first_entries[plot_range_low][4] - bias

        for i in range(plot_range_low, plot_range_high):

            axs.plot([swipe_log[i], swipe_log[i+1]], [yaxis[i], yaxis[i]], color="r", linestyle="--", linewidth=3)

            s_idx = int((swipe_log[i] - x_start) * 10)
            for idx_i in range(s_idx, 1201):
                buffer_arr[idx_i] -= 1

            if (i in first_entries_parsed and abs(swipe_log[i+1] - swipe_log[i] - first_entries_parsed[i][7]/1000.0) < 0.5) == False:
                scatter_x.append(swipe_log[i+1])
                scatter_y.append(i + 0.5)

            buffer_traces.append((swipe_log[i], -1))

            if i in first_entries_parsed.keys() and swipe_log[i] < first_entries_parsed[i][1]:
                draw_rebuffer(axs, min(first_entries_parsed[i][1], swipe_log[i+1]), swipe_log[i])

            if i in first_entries_parsed.keys():
                play_start_time = max(first_entries_parsed[i][1], swipe_log[i])

                second_entries_start = play_start_time + first_entries_parsed[i][7] / 1000

                if second_entries_start < swipe_log[i+1]:
                    if i in second_entries_parsed.keys():
                        rebuffer_finish = min(swipe_log[i+1], second_entries_parsed[i][1])


        for i in range(plot_range_low, plot_range_high):

            if i in first_entries_parsed.keys():
                draw_bar(axs, i, first_entries_parsed[i][0], first_entries_parsed[i][1], quality_to_color(first_entries_parsed[i][2]), False)


                s_idx = int((first_entries_parsed[i][1] - x_start) * 10)
                for idx_i in range(s_idx, 1201):
                    buffer_arr[idx_i] += 1

                buffer_traces.append((first_entries_parsed[i][1], 1))


                if i % 10 == 0 and i > plot_range_low:
                    axs.plot([first_entries_parsed[i][0], first_entries_parsed[i][0]], [0, 100], color="k", linestyle="--", linewidth=2)

            if i in second_entries_parsed.keys():
                axs.plot([first_entries_parsed[i][1], second_entries_parsed[i][0]], [i+0.5, i+0.5], color=(0.5, 0.5, 0.5), linestyle="--")
                draw_bar(axs, i, second_entries_parsed[i][0], second_entries_parsed[i][1], quality_to_color((second_entries_parsed[i][2])), True)

        legend_name = ["480p", "540p-low", "540p-high", "720p"]
        for i in range(4):
            axs.bar(-20, 1, color=cmaplist[i], label=legend_name[i])
        axs.plot([-20, -21], [1, 1], color="r", linestyle="--", linewidth =3, label="Video Play")

        buffer_length_dict = {}
        swipe_log_idx = 0
        for i in range(d_len):
            if i in first_entries_parsed.keys():

                while swipe_log_idx+1 < len(swipe_log) and swipe_log[swipe_log_idx+1] < first_entries_parsed[i][1]:

                    swipe_log_idx += 1

                buffer_length_dict[i] = i - swipe_log_idx

        axs.legend(loc='upper left', bbox_to_anchor=(0, 1.25), ncol=5)

        axs.set_ylim(plot_range_low, plot_range_high)

        x_start = first_entries[plot_range_low][4] - bias
        axs.set_xlim(x_start, x_start + 120)

        x_tics = [i + x_start for i in range(0, 121, 20)]
        x_name = ["0", "20", "40", "60", "80", "100", "120"]
        axs.set_xticks(x_tics)
        axs.set_xticklabels(x_name)

        axs.set_ylabel("Video index")
        axs.set_xlabel("Time (s)")

        axs.set_yticks([30, 40, 50])


        axs.set_yticklabels(["0", "10", "20"])

        #################################################################################

        # axs[1]
        plt.savefig(f"./order/{netid/2:.1f}-swipe-{swipeid}.png", bbox_inches='tight', dpi=200)

        plt.close()

        t1 = first_entries_parsed[plot_range_low][0] - x_start
        t2 = first_entries_parsed[plot_range_low + 4][1]  - x_start

        t3 = first_entries_parsed[plot_range_low + 9][1]  - x_start

        t4 = first_entries_parsed[plot_range_low + 10][0]  - x_start

        t5 = first_entries_parsed[plot_range_low + 17][1]  - x_start

        t6 = first_entries_parsed[plot_range_low + 19][1]  - x_start

        t7 = first_entries_parsed[plot_range_low + 20][0]  - x_start

        fig, axs = plt.subplots(1, 1, figsize=(30, 3))
        # plt.subplots_adjust(hspace=0.3)
        idxs = [0.1 * i for i in range(1201)]
        axs.plot(idxs, buffer_arr, color="b", linewidth=2)
        axs.plot([0, 1201], [0, 0], color="k", linewidth=2)

        axs.set_xlim(0, 120)
        axs.set_ylim(-1.2, 5.2)

        axs.set_yticks([-1, 0, 1, 2, 3, 4, 5])
        axs.set_ylabel("# future videos")
        axs.set_xlabel("Time (s)")

        draw_ramp(axs, t1, t2)
        draw_maintain(axs, t2, t3)
        draw_idle(axs, t3, t4)
        draw_ramp(axs, t4, t5)
        draw_maintain(axs, t5, t6)
        draw_idle(axs, t6, t7)
        draw_ramp(axs, t7, 120)
        # draw_ramp(axs, t1, t2)
        # axs.set_yticklabels(0, 120)

        plt.savefig(f"./order/{netid/2:.1f}-swipe-{swipeid}-buffer.png", bbox_inches='tight', dpi=200)

        plt.close()
