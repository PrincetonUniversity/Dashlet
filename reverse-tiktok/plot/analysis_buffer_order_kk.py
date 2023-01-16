import csv
import os.path

import numpy as np
import matplotlib.pyplot as plt
import random
from statsmodels.distributions.empirical_distribution import ECDF
from matplotlib.patches import Rectangle


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




def draw_bar(ax, i, start, end, barcolor):
    ax.add_patch(Rectangle((start, i), end-start, 1, color=barcolor))


def draw_rebuffer(ax, start, end):
    ax.add_patch(Rectangle((start, 0), end-start, 1000000000000, color=(181/255, 181/255, 181/255)))

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


for netid in range(10, 11):
    for swipeid in range(2, 7):

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


        yaxis = []

        for i in range(len(swipe_log)):
            swipe_log[i] -= bias
            tmp = 1
            yaxis.append(i + 0.5)

        for entry in first_entries:
            first_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]

        for entry in second_entries:
            second_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]

        d_len = first_entries[-1][2] + 1


        plt.figure(figsize=(30, 8))

        fig, ax = plt.subplots(3, 1, figsize=(30, 8), gridspec_kw={'height_ratios': [2, 1, 2]})

        scatter_x = []
        scatter_y = []

        buffer_traces = []

        for i in range(d_len):
            if i in first_entries_parsed.keys():
                # draw_bar(ax, i, first_entries_parsed[i][0], first_entries_parsed[i][1], quality_to_color(first_entries_parsed[i][2]))
                scatter_x.append(first_entries_parsed[i][3])
                scatter_y.append(i + 0.5)

            if i in second_entries_parsed.keys():
                # draw_bar(ax, i, second_entries_parsed[i][0], second_entries_parsed[i][1], quality_to_color((second_entries_parsed[i][2])))
                scatter_x.append(second_entries_parsed[i][3])
                scatter_y.append(i + 0.5)


        for i in range(1, len(swipe_log) - 1):

            ax.plot([swipe_log[i], swipe_log[i+1]], [yaxis[i]%10, yaxis[i]%10], "k--")

            buffer_traces.append((swipe_log[i], -1))

            if i in first_entries_parsed.keys() and swipe_log[i] < first_entries_parsed[i][1]:
                draw_rebuffer(ax, first_entries_parsed[i][1], swipe_log[i])
                # tmp = 1


        for i in range(d_len):
            if i in first_entries_parsed.keys():
                draw_bar(ax, i%10, first_entries_parsed[i][0], first_entries_parsed[i][1], quality_to_color(first_entries_parsed[i][2]))
                scatter_x.append(first_entries_parsed[i][3])
                scatter_y.append(i%10 + 0.5)

                buffer_traces.append((first_entries_parsed[i][1], 1))

            if i in second_entries_parsed.keys():
                draw_bar(ax, i%10, second_entries_parsed[i][0], second_entries_parsed[i][1], quality_to_color((second_entries_parsed[i][2])))
                scatter_x.append(second_entries_parsed[i][3])
                scatter_y.append(i%10 + 0.5)

        ax.scatter(scatter_x, scatter_y, color="k")




        # plt.bar(-20, 1, color="b", label="Download Second Half")

        for i in range(4):
            ax.bar(-20, 1, color=cmaplist[i], label=f"Download Bitrate {i+1}")
        ax.plot([-20, -21], [1, 1], "k--", label="Video Play")

        # ax.scatter(scatter_x, scatter_y, color="k", zorder=2)

        ax.legend()

        plot_range_low = 0
        plot_range_high = 25
        ax.set_ylim(plot_range_low, 11)
        ax.set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Video index")

        net_data_all = []

        for i in range(5):
            net_data_all.extend(net_data)

        time_idx = []

        for i in range(len(net_data_all)):

            time_idx.append(i+trace_start_time)

        ax[1].plot(time_idx, net_data_all, "k--")


        # for i in range(d_len):
        #     if i in first_entries_parsed.keys():
        #         ax[1].plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [first_entries_parsed[i][4], first_entries_parsed[i][4]], "r--")
        #
        #     if i in second_entries_parsed.keys():
        #         ax[1].plot([second_entries_parsed[i][0], second_entries_parsed[i][1]], [second_entries_parsed[i][4], second_entries_parsed[i][4]], "r--")
        # ax[1].set_ylim(0, 75)
        ax[1].set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
        ax[1].set_xlabel("Time (s)")
        ax[1].set_ylabel("Throughput (Mbps)")


        for i in range(d_len):
            if i in first_entries_parsed.keys():
                for b_rate in first_entries_parsed[i][8]:
                    ax[2].plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [b_rate/1000000, b_rate/1000000], "b--")
                ax[2].plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [first_entries_parsed[i][9]/1000000, first_entries_parsed[i][9]/1000000], "r")

                # ax[2].plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [first_entries_parsed[i][4], first_entries_parsed[i][4]], "r--")

        ax[2].set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
        ax[2].set_ylim(0, 2)
        ax[2].set_xlabel("Time (s)")
        ax[2].set_ylabel("Bitrate (Mbps)")
        buffer_traces.sort()

        time_num = 0
        buffer_num = 0

        # for i in range(1, len(buffer_traces)):
        #     ax[2].plot([time_num, buffer_traces[i][0]], [buffer_num, buffer_num], 'k')
        #
        #     time_num = buffer_traces[i][0]
        #
        #     ax[2].plot([time_num, time_num], [buffer_num, buffer_num + buffer_traces[i][1]], 'k')
        #
        #     buffer_num = buffer_num + buffer_traces[i][1]
        #
        # ax[2].set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
        # ax[2].set_xlabel("Time (s)")
        # ax[2].set_ylabel("# buffer video")



        # plt.show()
        plt.savefig(f"./order/{netid/2:.1f}-swipe-{swipeid}.png", bbox_inches='tight')

        plt.close()

        play_string_arr = []


        ymax = 0
        plt.figure(figsize=(20, 6))

        fig, ax = plt.subplots(1, 1, figsize=(20, 6))

        for i in range(plot_range_low, plot_range_high+1):
            if i in first_entries_parsed.keys():
                first_bytes = first_entries_parsed[i][5]

                if first_bytes == 1024000:
                    first_bytes += 48000 * ((i % 6) / 6)

                ax.plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [0, first_bytes], color=cmaplist2[i%6])
                # draw_bar(ax, i, first_entries_parsed[i][0], first_entries_parsed[i][1], quality_to_color(first_entries_parsed[i][2]))

            if i in second_entries_parsed.keys():
                ax.plot([second_entries_parsed[i][0], second_entries_parsed[i][1]], [0, second_entries_parsed[i][5]], color=cmaplist2[i%6], linestyle="--")
                ymax = max(ymax, second_entries_parsed[i][5])

        for i in range(plot_range_low, plot_range_high+1):

            if i in first_entries_parsed.keys():

                first_play_start_time = max(first_entries_parsed[i][1], swipe_log[i])

                view_time = max(swipe_log[i+1] - first_play_start_time, 0)

                first_bytes = first_entries_parsed[i][5]

                ymax = max(first_bytes, ymax)

                if first_bytes == 1024000:
                    first_bytes += 48000 * ((i % 6) / 6)

                if first_entries_parsed[i][1] < swipe_log[i]:
                    ax.plot([first_entries_parsed[i][1], swipe_log[i]], [first_bytes, first_bytes], color=cmaplist2[i%6])
                else:
                    draw_rebuffer(ax, swipe_log[i], first_entries_parsed[i][1])

                if view_time <= first_entries_parsed[i][7] / 1000.0:

                    view_bytes = view_time / (first_entries_parsed[i][7] / 1000.0) * first_bytes

                    ax.plot([first_play_start_time, swipe_log[i+1]], [first_bytes, first_bytes - view_bytes], color=cmaplist2[i%6])

                    play_string_arr.append([(first_play_start_time, first_bytes), (swipe_log[i+1], first_bytes - view_bytes), 1])

                else:

                    ax.plot([first_play_start_time, first_play_start_time + first_entries_parsed[i][7] / 1000.0], [first_bytes, 0], color=cmaplist2[i%6])

                    play_string_arr.append([(first_play_start_time, first_bytes), (first_play_start_time + first_entries_parsed[i][7] / 1000.0, 0), 0])

                    if i in second_entries_parsed.keys():

                        second_play_start_time = max(first_play_start_time + first_entries_parsed[i][7] / 1000, second_entries_parsed[i][1])

                        view_time2 = max(view_time + first_play_start_time - second_play_start_time, 0)

                        second_bytes = second_entries_parsed[i][5]

                        ymax = max(ymax, second_bytes)

                        if second_entries_parsed[i][1] < first_play_start_time + first_entries_parsed[i][7] / 1000:
                            ax.plot([second_entries_parsed[i][1], first_play_start_time + first_entries_parsed[i][7] / 1000], [second_bytes, second_bytes], color=cmaplist2[i%6], linestyle="--")
                        else:
                            draw_rebuffer(ax, first_play_start_time + first_entries_parsed[i][7] / 1000, second_entries_parsed[i][1])

                        view_bytes2 = view_time2 / (second_entries_parsed[i][7] / 1000.0) * second_entries_parsed[i][5]

                        ax.plot([second_play_start_time, second_play_start_time + view_time2], [second_bytes, second_bytes - view_bytes2], color=cmaplist2[i%6], linestyle="--")

                        play_string_arr.append([(second_play_start_time, second_bytes), (second_play_start_time + view_time2, second_bytes - view_bytes2), 1])


        for i in range(len(play_string_arr)):
            ax.plot([play_string_arr[i][0][0], play_string_arr[i][1][0]], [play_string_arr[i][0][1], play_string_arr[i][1][1]], linewidth=6, zorder=0, color=(0.5, 0.5, 0.5))

            if i > 0:
                ax.plot([play_string_arr[i-1][1][0], play_string_arr[i][0][0]], [play_string_arr[i-1][1][1], play_string_arr[i][0][1]], linewidth=6, zorder=0, color=(0.5, 0.5, 0.5))

            if play_string_arr[i][2] == 1:
                ax.scatter([play_string_arr[i][1][0]], [play_string_arr[i][1][1]], color="r", marker="o", s=20)

        ax.set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
        ax.set_ylim(0, ymax + 10000)

        ax.set_xlabel("Time")
        ax.set_ylabel("Bytes")


        plt.savefig(f"./order/playback-{netid/2:.1f}-swipe-{swipeid}.png", bbox_inches='tight')

        plt.close()





