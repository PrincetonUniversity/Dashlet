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


# for netid in range(19, 20):
#     for swipeid in range(3, 7):
# 
#         net_data = load_network(f"../traces/network/trace-{netid/2:.1f}.down")
#         foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
#         play_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-play.csv"
#         download_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-download.csv"
#         swipe_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-swipe.log"
#         start_time_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-start-time.log"
# 
# 
# 
#         print(foldername)
# 
# 
# 
#         swipe_log, first_entries, second_entries = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name)
# 
#         if len(first_entries) < 10:
#             continue
# 
#         if os.path.exists(foldername + start_time_name):
#             start_time = np.loadtxt(foldername + start_time_name)
# 
#             print(swipe_log[1] - start_time)
# 
#         bias = first_entries[0][4]
# 
#         trace_start_time = swipe_log[1] - trace_start_offset - bias
# 
#         first_entries_parsed = {}
#         second_entries_parsed = {}
# 
# 
#         yaxis = []
# 
#         for i in range(len(swipe_log)):
#             swipe_log[i] -= bias
#             tmp = 1
#             yaxis.append(i + 0.5)
# 
#         for entry in first_entries:
# 
#             first_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8]]
# 
#         for entry in second_entries:
#             second_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8]]
# 
#             # if entry[2]+1 < len(swipe_log):
#                 # if swipe_log[entry[2]+1] < second_entries_parsed[entry[2]][1]:
#                 #     second_entries_parsed[entry[2]][1] = swipe_log[entry[2]+1]
# 
#         d_len = first_entries[-1][2] + 1
# 
# 
#         plt.figure(figsize=(40, 10))
# 
# 
#         fig, ax = plt.subplots(2, 1, figsize=(20, 6), gridspec_kw={'height_ratios': [3, 1]})
# 
#         scatter_x = []
#         scatter_y = []
# 
# 
#         buffer_traces = []
# 
#         for i in range(d_len):
#             if i in first_entries_parsed.keys():
#                 # draw_bar(ax, i, first_entries_parsed[i][0], first_entries_parsed[i][1], quality_to_color(first_entries_parsed[i][2]))
#                 scatter_x.append(first_entries_parsed[i][3])
#                 scatter_y.append(i + 0.5)
# 
#             if i in second_entries_parsed.keys():
#                 # draw_bar(ax, i, second_entries_parsed[i][0], second_entries_parsed[i][1], quality_to_color((second_entries_parsed[i][2])))
#                 scatter_x.append(second_entries_parsed[i][3])
#                 scatter_y.append(i + 0.5)
# 
# 
# 
# 
#         for i in range(1, len(swipe_log) - 1):
# 
#             ax.plot([swipe_log[i], swipe_log[i+1]], [yaxis[i], yaxis[i]], "k--")
# 
#             buffer_traces.append((swipe_log[i], -1))
# 
#             if i in first_entries_parsed.keys() and swipe_log[i] < first_entries_parsed[i][1]:
#                 draw_rebuffer(ax, first_entries_parsed[i][1], swipe_log[i])
#                 # tmp = 1
# 
# 
#         for i in range(d_len):
#             if i in first_entries_parsed.keys():
#                 draw_bar(ax, i, first_entries_parsed[i][0], first_entries_parsed[i][1], quality_to_color(first_entries_parsed[i][2]))
#                 scatter_x.append(first_entries_parsed[i][3])
#                 scatter_y.append(i + 0.5)
# 
#                 if i % 10 == 0:
#                     ax.plot([first_entries_parsed[i][0], first_entries_parsed[i][0]], [0, 1000000], "k--")
# 
#                 buffer_traces.append((first_entries_parsed[i][1], 1))
# 
#             if i in second_entries_parsed.keys():
#                 draw_bar(ax, i, second_entries_parsed[i][0], second_entries_parsed[i][1], quality_to_color((second_entries_parsed[i][2])))
#                 scatter_x.append(second_entries_parsed[i][3])
#                 scatter_y.append(i + 0.5)
# 
#         # ax.scatter(scatter_x, scatter_y, color="k")
# 
# 
# 
# 
#         # plt.bar(-20, 1, color="b", label="Download Second Half")
# 
#         for i in range(4):
#             ax.bar(-20, 1, color=cmaplist[i], label=f"Download Bitrate {i+1}")
#         ax.plot([-20, -21], [1, 1], "k--", label="Video Play")
# 
#         # ax.scatter(scatter_x, scatter_y, color="k", zorder=2)
# 
#         ax.legend()
# 
#         plot_range_low = 0
#         plot_range_high = 55
#         ax.set_ylim(plot_range_low, plot_range_high)
#         ax.set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
#         ax.set_xlabel("Time (s)")
#         ax.set_ylabel("Video index")
# 
#         net_data_all = []
# 
#         for i in range(5):
#             net_data_all.extend(net_data)
# 
#         time_idx = []
# 
#         for i in range(len(net_data_all)):
# 
#             time_idx.append(i+trace_start_time)
# 
#         ax[1].plot(time_idx, net_data_all, "k--")
# 
# 
#         for i in range(d_len):
#             if i in first_entries_parsed.keys():
#                 ax[1].plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [first_entries_parsed[i][4], first_entries_parsed[i][4]], "r--")
# 
#             if i in second_entries_parsed.keys():
#                 ax[1].plot([second_entries_parsed[i][0], second_entries_parsed[i][1]], [second_entries_parsed[i][4], second_entries_parsed[i][4]], "r--")
#         # ax[1].set_ylim(0, 75)
#         ax[1].set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
#         ax[1].set_xlabel("Time (s)")
#         ax[1].set_ylabel("Throughput (Mbps)")
# 
# 
#         buffer_traces.sort()
# 
#         time_num = 0
#         buffer_num = 0
# 
#         plt.savefig(f"./state/{netid/2:.1f}-swipe-{swipeid}.png", bbox_inches='tight')
# 
#         plt.close()


ramp_up_dist = []
buffer_maintain_dist = []
idle_dist = []

for netid in range(2, 6):
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


        plt.figure(figsize=(30, 5))

        fig, ax = plt.subplots(2, 1, figsize=(30, 5), gridspec_kw={'height_ratios': [2, 1]})
        plt.subplots_adjust(hspace=0.3)


        scatter_x = []
        scatter_y = []

        buffer_traces = []

        # for i in range(d_len):
        #     if i in first_entries_parsed.keys():
        #         # draw_bar(ax, i, first_entries_parsed[i][0], first_entries_parsed[i][1], quality_to_color(first_entries_parsed[i][2]))
        #         scatter_x.append(first_entries_parsed[i][3])
        #         scatter_y.append(i + 0.5)
        #
        #     if i in second_entries_parsed.keys():
        #         # draw_bar(ax, i, second_entries_parsed[i][0], second_entries_parsed[i][1], quality_to_color((second_entries_parsed[i][2])))
        #         scatter_x.append(second_entries_parsed[i][3])
        #         scatter_y.append(i + 0.5)


        for i in range(1, len(swipe_log) - 1):

            ax[0].plot([swipe_log[i], swipe_log[i+1]], [yaxis[i]%10, yaxis[i]%10], "k--")

            if (i in first_entries_parsed and abs(swipe_log[i+1] - swipe_log[i] - first_entries_parsed[i][7]/1000.0) < 0.5) == False:
                scatter_x.append(swipe_log[i+1])
                scatter_y.append(i%10 + 0.5)


            buffer_traces.append((swipe_log[i], -1))

            if i in first_entries_parsed.keys() and swipe_log[i] < first_entries_parsed[i][1]:
                draw_rebuffer(ax[0], min(first_entries_parsed[i][1], swipe_log[i+1]), swipe_log[i])

            if i in first_entries_parsed.keys():
                play_start_time = max(first_entries_parsed[i][1], swipe_log[i])

                second_entries_start = play_start_time + first_entries_parsed[i][7] / 1000

                if second_entries_start < swipe_log[i+1]:
                    if i in second_entries_parsed.keys():
                        rebuffer_finish = min(swipe_log[i+1], second_entries_parsed[i][1])

                        if rebuffer_finish > second_entries_start:
                            if rebuffer_finish - second_entries_start > 0.5:
                                draw_rebuffer(ax[0], second_entries_start, rebuffer_finish)
                        tmp = 1
                    else:
                        if swipe_log[i+1] - second_entries_start > 0.5:
                            draw_rebuffer(ax[0], second_entries_start, swipe_log[i+1])


        for i in range(d_len):
            if i in first_entries_parsed.keys():
                draw_bar(ax[0], i%10, first_entries_parsed[i][0], first_entries_parsed[i][1], quality_to_color(first_entries_parsed[i][2]), False)
                # scatter_x.append(first_entries_parsed[i][3])
                # scatter_y.append(i%10 + 0.5)

                buffer_traces.append((first_entries_parsed[i][1], 1))

            if i in second_entries_parsed.keys():
                draw_bar(ax[0], i%10, second_entries_parsed[i][0], second_entries_parsed[i][1], quality_to_color((second_entries_parsed[i][2])), True)
                # scatter_x.append(second_entries_parsed[i][3])
                # scatter_y.append(i%10 + 0.5)

        ax[0].scatter(scatter_x, scatter_y, color="k", zorder=200)

        # plt.bar(-20, 1, color="b", label="Download Second Half")

        for i in range(4):
            ax[0].bar(-20, 1, color=cmaplist[i], label=f"Download Bitrate {i+1}")
        ax[0].plot([-20, -21], [1, 1], "k--", label="Video Play")

        # ax[0].scatter(scatter_x, scatter_y, color="k", zorder=2)


        buffer_length_dict = {}
        swipe_log_idx = 0
        for i in range(d_len):
            if i in first_entries_parsed.keys():

                while swipe_log_idx+1 < len(swipe_log) and swipe_log[swipe_log_idx+1] < first_entries_parsed[i][1]:

                    swipe_log_idx += 1

                buffer_length_dict[i] = i - swipe_log_idx


        if True:

            for i in range(int(d_len/10)):
                if (i * 10) not in first_entries_parsed.keys():
                    continue
                ramp_up_time_start = first_entries_parsed[i*10][0]

                buffer_maintain_time = -1

                for j in range(10):
                    if (i * 10 + j) in first_entries_parsed.keys() and buffer_length_dict[i * 10 + j] == 5:
                        buffer_maintain_time = first_entries_parsed[i * 10 + j][1]
                        break

                if (i * 10 + 9) not in first_entries_parsed.keys():
                    continue
                idle_time_start = first_entries_parsed[i*10+9][1]

                if (i * 10 + 10) not in first_entries_parsed.keys():
                    continue

                next_ramp_up_time_start = first_entries_parsed[i*10 + 10][0]

                if buffer_maintain_time == -1:
                    buffer_maintain_time = next_ramp_up_time_start
                    idle_time_start = next_ramp_up_time_start

                ramp_up_duration = buffer_maintain_time - ramp_up_time_start
                buffer_maintain_duration = idle_time_start - buffer_maintain_time
                idle_duration = next_ramp_up_time_start - idle_time_start
                total_duration = next_ramp_up_time_start - ramp_up_time_start

                ramp_up_percentage = ramp_up_duration / total_duration
                buffer_maintain_percentage = buffer_maintain_duration / total_duration
                idle_percentage = idle_duration / total_duration

                ramp_up_dist.append(ramp_up_percentage)
                buffer_maintain_dist.append(buffer_maintain_percentage)
                idle_dist.append(idle_percentage)

                draw_ramp(ax[0], ramp_up_time_start, ramp_up_time_start + ramp_up_duration)
                draw_maintain(ax[0], ramp_up_time_start + ramp_up_duration, ramp_up_time_start + ramp_up_duration + buffer_maintain_duration)
                draw_idle(ax[0], ramp_up_time_start + ramp_up_duration + buffer_maintain_duration, next_ramp_up_time_start)

        ax[0].legend(loc='upper left', bbox_to_anchor=(0, 1.4), ncol=5)

        plot_range_low = 0
        plot_range_high = 70
        ax[0].set_ylim(plot_range_low, 11)
        ax[0].set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
        # ax[0].set_xlabel("Time (s)")
        ax[0].set_ylabel("Video index")

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
        ax[1].set_ylabel("Tput (Mbps)")


        # for i in range(d_len):
        #     if i in first_entries_parsed.keys():
        #         for b_rate in first_entries_parsed[i][8]:
        #             ax[2].plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [b_rate/1000000, b_rate/1000000], "b--")
        #         ax[2].plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [first_entries_parsed[i][9]/1000000, first_entries_parsed[i][9]/1000000], "r")
        #
        #         # ax[2].plot([first_entries_parsed[i][0], first_entries_parsed[i][1]], [first_entries_parsed[i][4], first_entries_parsed[i][4]], "r--")
        #
        # ax[2].set_xlim(first_entries[plot_range_low][4] - bias, swipe_log[plot_range_high + 1])
        # ax[2].set_ylim(0, 2)
        # ax[2].set_xlabel("Time (s)")
        # ax[2].set_ylabel("Bitrate (Mbps)")
        # buffer_traces.sort()
        #
        # time_num = 0
        # buffer_num = 0
        #
        plt.savefig(f"./order/{netid/2:.1f}-swipe-{swipeid}.png", bbox_inches='tight', dpi=200)

        plt.close()

        play_string_arr = []


from statsmodels.distributions.empirical_distribution import ECDF


# fig, ax = plt.subplots(1, 3, figsize=(20, 6))
#
# ecdf1 = ECDF(ramp_up_dist)
# ax.plot(ecdf1.x, ecdf1.y, label="Ramp up percentage", lw=3, color="r")
#
# ax.legend()
#
# ax.set_xlabel("Percentage")
# ax.set_ylabel("CDF")
#
# ax.set_xlim([0, 1])
#
# ecdf2 = ECDF(buffer_maintain_dist)
# ax[1].plot(ecdf2.x, ecdf2.y, label="Buffer maintain percentage", lw=3, color="b")
#
# ax[1].legend()
#
# ax[1].set_xlabel("Percentage")
# ax[1].set_ylabel("CDF")
#
# ax[1].set_xlim([0, 1])
#
# ecdf3 = ECDF(idle_dist)
# ax[2].plot(ecdf3.x, ecdf3.y, label="Idle percentage", lw=3, color="g")
# ax[2].legend()
#
# ax[2].set_xlabel("Percentage")
# ax[2].set_ylabel("CDF")
# ax[2].set_xlim([0, 1])
# plt.savefig(f"./state/state_percentage_cdf.png", bbox_inches='tight')
# plt.close()
#
#
# fig, ax = plt.subplots(1, 1, figsize=(8, 5))
#
#
# combined = []
#
# for i in range(len(ramp_up_dist)):
#     combined.append((ramp_up_dist[i], ramp_up_dist[i] + buffer_maintain_dist[i], 1))
#
# combined = sorted(combined)
#
# line1 = []
# line2 = []
# line3 = []
# for i in range(len(combined)):
#     line1.append(combined[i][0])
#     line2.append(combined[i][1])
#     line3.append(combined[i][2])
#
#
# xline = [i for i in range(len(line1))]
#
#
# ax.fill_between(xline, line1, color="r")
# ax.fill_between(xline, line1, line2, color="b")
# ax.fill_between(xline, line2, line3, color="g")
#
# ax.set_ylim([0, 1])
#
# plt.savefig(f"./state/state_percentage_combined.png", bbox_inches='tight')
# plt.close()


tmp = 1






