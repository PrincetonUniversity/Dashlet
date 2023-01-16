import csv
import os.path

import numpy as np
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF
from matplotlib.patches import Rectangle

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


out_folder = "./qoe/"

first_part_time_dis = []

effect_download_dis = []
download_percentage_dis = []

trace_id_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 21, 22, 23, 24, 25]

for traceid in trace_id_list:
    for swipeid in range(2, 6):

        effect_download = 0
        total_download = 0
        total_download_time = 0

        foldername = f"../data/ifi-{traceid}-swipe-{swipeid}/"
        play_log_name = f"ifi-{traceid}-swipe-{swipeid}-play.csv"
        download_log_name = f"ifi-{traceid}-swipe-{swipeid}-download.csv"
        swipe_log_name = f"ifi-{traceid}-swipe-{swipeid}-swipe.log"
        start_time_name = f"ifi-{traceid}-swipe-{swipeid}-start-time.log"

        out_file = f"{out_folder}wifi-{traceid}-swipe-{swipeid}.txt"

        fd = open(out_file, "w")

        print(foldername)

        swipe_log, first_entries, second_entries = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name)

        # if len(first_entries) < 10:
        #     continue

        if os.path.exists(foldername + start_time_name):
            start_time = np.loadtxt(foldername + start_time_name)

            print(swipe_log[1] - start_time)

        swipe_log[0] = swipe_log[1] - 60

        bias = swipe_log[0]

        first_entries_parsed = {}
        second_entries_parsed = {}

        for i in range(len(swipe_log)):
            swipe_log[i] -= bias

        for entry in first_entries:
            first_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]

        for entry in second_entries:
            second_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]


        for i in range(80):

            this_total_download = 0
            firstchunk_bytes = 0
            rebuffering = 0
            if i in first_entries_parsed.keys():

                this_total_download += first_entries_parsed[i][5]
                total_download_time += first_entries_parsed[i][1] - first_entries_parsed[i][0]

                firstchunk_bytes = first_entries_parsed[i][6]


                download_finish_time = first_entries_parsed[i][1]

                chunk_duration = first_entries_parsed[i][7] / 1000

                total_duration = chunk_duration

                view_time = max(swipe_log[i+1] - max(swipe_log[i], download_finish_time), 0)

                rebuffering = max(0, download_finish_time-swipe_log[i])
                rebuffering = min(rebuffering, (swipe_log[i+1] - swipe_log[i]))

                first_part_time = chunk_duration * first_entries_parsed[i][5] / first_entries_parsed[i][6]

                first_part_time_dis.append(first_part_time)

                if i in second_entries_parsed.keys():
                    this_total_download += second_entries_parsed[i][5]
                    total_download_time += (second_entries_parsed[i][1] - second_entries_parsed[i][0])

                    total_duration += second_entries_parsed[i][7] / 1000

                    if view_time > first_part_time:
                        second_view_start = first_part_time + max(swipe_log[i], download_finish_time)

                        rebuffering += max(0, second_entries_parsed[i][1]-second_view_start)
                        rebuffering = min(rebuffering, (swipe_log[i+1] - swipe_log[i]))



                real_view_time = max(min(swipe_log[i+1] - swipe_log[i] - rebuffering, chunk_duration), 0)

                reward = firstchunk_bytes * real_view_time / chunk_duration

                fd.write(f"{rebuffering} {int(reward/1000)} {i} {swipe_log[i+1] - swipe_log[i]}\n")
            else:
                rebuffering = max(swipe_log[i+1] - swipe_log[i], 0)
                real_view_time = 0

                fd.write(f"{rebuffering} {0} {i} {swipe_log[i+1] - swipe_log[i]}\n")

                # total_download_time += max(swipe_log[i+1] - swipe_log[i], 0) * 0.7

            if this_total_download > 0 and i>0:
                total_download += this_total_download
                effect_download += this_total_download * real_view_time / total_duration


        total_time = swipe_log[80] - swipe_log[0]

        if total_download > 0.01:
            effect_download_dis.append((traceid, swipeid, effect_download / total_download))
            download_percentage_dis.append((traceid, swipeid, total_download_time / total_time))
        else:
            effect_download_dis.append((traceid, swipeid, 0))
            download_percentage_dis.append((traceid, swipeid, -1))

        fd.close()


fd = open("effect-download-tt-wifi.txt", "w")

for item in effect_download_dis:
    fd.write(f"{item[0]} {item[1]} {item[2]}\n")

fd.close()

# ecdf_effect_download = ECDF(effect_download_dis)
#
# plt.plot(ecdf_effect_download.x, ecdf_effect_download.y, label="TikTok", lw=3)
# plt.legend()
# plt.grid()
# # plt.show()
# plt.ylabel("CDF")
# plt.xlabel("Viewed data / Downloaded data")
# plt.xlim([0, 1])
# plt.savefig("effect-download.png", bbox_inches='tight')
# plt.close()


fd = open("download-percentage-tt-wifi.txt", "w")

for item in download_percentage_dis:
    fd.write(f"{item[0]} {item[1]} {item[2]}\n")

fd.close()





# import csv
# import os.path
#
# import numpy as np
# import matplotlib.pyplot as plt
# from statsmodels.distributions.empirical_distribution import ECDF
# from matplotlib.patches import Rectangle
#
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
# def analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name):
#
#     play_log = []
#     download_log = []
#     swipe_log = [0]
#
#     uri_dict = {}
#
#     uri_to_quality = {}
#     uri_to_bitrate = {}
#     uri_to_bitrate_list = {}
#
#     with open(foldername+swipe_log_name, newline='') as csvfile:
#         spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#         for row in spamreader:
#             swipe_log.append(float(row[1]))
#
#     with open(foldername+play_log_name, newline='') as csvfile:
#         spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
#         for row in spamreader:
#             bitrates = row[3].split("&")
#
#             encode_uri = row[4].split("&")
#
#             quality_string = row[6].split("&")
#
#             parsed_row = [int(row[0]), row[1], int(row[2]), [int(bitrate) for bitrate in bitrates], encode_uri, row[5]]
#
#             for i in range(len(encode_uri)):
#                 uri_dict[encode_uri[i]] = (int(row[0]), int(i/2), len(bitrates))
#                 uri_to_quality[encode_uri[i]] = quality_string[int(i/2)]
#                 uri_to_bitrate[encode_uri[i]] = int(bitrates[int(i/2)])
#                 uri_to_bitrate_list[encode_uri[i]] = [int(bitrates[j]) for j in range(len(bitrates))]
#
#             play_log.append(parsed_row)
#
#     play_idx = 0
#
#     max_download_chunk = 0
#
#     download_progress = [(0, 0) for i in range(len(play_log))]
#
#     throughput_all = []
#
#     first_entries = []
#     second_entries = []
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
#                 bitrate_combo = (bitrate_decision, download_metadata[1], download_metadata[2] - 1)
#
#                 size_in_bytes = ranges[1] - ranges[0]
#
#                 total_size_in_bytes = int(play_log[downloadIdx][2] * uri_to_bitrate[row[IDX_DOWNLOAD_URI]] / 1000 / 8)
#
#
#                 if size_in_bytes == 0:
#                     size_in_bytes = total_size_in_bytes
#
#                 # if ranges[0] == 1024000:
#                 #     size_in_bytes = size_in_bytes + 100000 * ((downloadIdx%6) / 6)
#                 throughput_est = size_in_bytes * 8 / 1000 / 1000 / (float(row[IDX_RESPONSE_END]) - float(row[IDX_RESPONSE_START]))
#
#                 chunk_duration = size_in_bytes / total_size_in_bytes * play_log[downloadIdx][2]
#
#                 # IDX_REQUEST_START
#                 if ranges[0] != 1024000:
#                     first_entries.append([
#                         float(row[IDX_RESPONSE_START]),
#                         float(row[IDX_RESPONSE_END]),
#                         downloadIdx,
#                         uri_to_quality[row[IDX_DOWNLOAD_URI]],
#                         float(row[IDX_REQUEST_START]),
#                         throughput_est,
#                         size_in_bytes,
#                         total_size_in_bytes,
#                         chunk_duration,
#                         uri_to_bitrate_list[row[IDX_DOWNLOAD_URI]],
#                         bitrate_decision
#                     ])
#                 else:
#                     second_entries.append([
#                         float(row[IDX_RESPONSE_START]),
#                         float(row[IDX_RESPONSE_END]),
#                         downloadIdx,
#                         uri_to_quality[row[IDX_DOWNLOAD_URI]],
#                         float(row[IDX_REQUEST_START]),
#                         throughput_est,
#                         size_in_bytes,
#                         total_size_in_bytes,
#                         chunk_duration,
#                         uri_to_bitrate_list[row[IDX_DOWNLOAD_URI]],
#                         bitrate_decision
#                     ])
#
#     return swipe_log, first_entries, second_entries
#
#
# out_folder = "./qoe/"
#
# first_part_time_dis = []
#
# effect_download_dis = []
# download_percentage_dis = []
#
# for traceid in range(13):
#     for swipeid in range(2, 6):
#
#         effect_download = 0
#         total_download = 0
#         total_download_time = 0
#
#         foldername = f"../data/ifi-{traceid}-swipe-{swipeid}/"
#         play_log_name = f"ifi-{traceid}-swipe-{swipeid}-play.csv"
#         download_log_name = f"ifi-{traceid}-swipe-{swipeid}-download.csv"
#         swipe_log_name = f"ifi-{traceid}-swipe-{swipeid}-swipe.log"
#         start_time_name = f"ifi-{traceid}-swipe-{swipeid}-start-time.log"
#
#         out_file = f"{out_folder}wifi-{traceid}-swipe-{swipeid}.txt"
#
#         fd = open(out_file, "w")
#
#         print(foldername)
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
#         first_entries_parsed = {}
#         second_entries_parsed = {}
#
#         yaxis = []
#
#         for i in range(len(swipe_log)):
#             swipe_log[i] -= bias
#             tmp = 1
#             yaxis.append(i + 0.5)
#
#         for entry in first_entries:
#             first_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]
#
#         for entry in second_entries:
#             second_entries_parsed[entry[2]] = [entry[0] - bias, entry[1] - bias, entry[3], entry[4] - bias, entry[5], entry[6], entry[7], entry[8], entry[9], entry[10]]
#
#         if 0 not in first_entries_parsed.keys():
#             print(out_file)
#             continue
#         swipe_log[0] = first_entries_parsed[0][1]
#
#         i = 0
#
#         for fi in range(80):
#
#             this_total_download = 0
#             if fi in first_entries_parsed.keys():
#                 i = fi
#
#                 this_total_download += first_entries_parsed[i][5]
#                 total_download_time += first_entries_parsed[i][1] - first_entries_parsed[i][0]
#
#
#             download_finish_time = first_entries_parsed[i][1]
#
#             chunk_duration = first_entries_parsed[i][7] / 1000
#
#             total_duration = chunk_duration
#
#             view_time = max(swipe_log[i+1] - max(swipe_log[i], download_finish_time), 0)
#
#             rebuffering = max(0, download_finish_time-swipe_log[i])
#
#             first_part_time = chunk_duration * first_entries_parsed[i][5] / first_entries_parsed[i][6]
#
#             first_part_time_dis.append(first_part_time)
#
#             if i in second_entries_parsed.keys():
#                 this_total_download += second_entries_parsed[i][5]
#                 total_download_time += (second_entries_parsed[i][1] - second_entries_parsed[i][0])
#
#                 total_duration += second_entries_parsed[i][7] / 1000
#
#                 if view_time > first_part_time:
#                     second_view_start = first_part_time + max(swipe_log[i], download_finish_time)
#
#                     rebuffering += max(0, second_entries_parsed[i][1]-second_view_start)
#
#
#             real_view_time = max(min(swipe_log[i+1] - swipe_log[i] - rebuffering, chunk_duration), 0)
#
#             reward = first_entries_parsed[i][6] * real_view_time / chunk_duration
#             tmp = 1
#
#             fd.write(f"{rebuffering} {int(reward/1000)} {i} {swipe_log[i+1] - swipe_log[i]}\n")
#
#             if this_total_download > 0 and i>0:
#                 total_download += this_total_download
#                 effect_download += this_total_download * real_view_time / total_duration
#
#         effect_download_dis.append((traceid, swipeid, effect_download / total_download))
#
#         total_time = first_entries_parsed[i][1] - first_entries_parsed[0][0]
#
#         download_percentage_dis.append((traceid, swipeid, total_download_time / total_time))
#
#         fd.close()
#
#
# fd = open("effect-download-tt-wifi.txt", "w")
#
# for item in effect_download_dis:
#     fd.write(f"{item[0]} {item[1]} {item[2]}\n")
#
# fd.close()
#
# # ecdf_effect_download = ECDF(effect_download_dis)
# #
# # plt.plot(ecdf_effect_download.x, ecdf_effect_download.y, label="TikTok", lw=3)
# # plt.legend()
# # plt.grid()
# # # plt.show()
# # plt.ylabel("CDF")
# # plt.xlabel("Viewed data / Downloaded data")
# # plt.xlim([0, 1])
# # plt.savefig("effect-download.png", bbox_inches='tight')
# # plt.close()
#
#
# fd = open("download-percentage-tt-wifi.txt", "w")
#
# for item in download_percentage_dis:
#     fd.write(f"{item[0]} {item[1]} {item[2]}\n")
#
# fd.close()
#
#
# # ecdf_download_percentage = ECDF(download_percentage_dis)
# # plt.plot(ecdf_download_percentage.x, ecdf_download_percentage.y, label="TikTok", lw=3)
# # plt.legend()
# # plt.grid()
# # # plt.show()
# # plt.ylabel("CDF")
# # plt.xlim([0, 1])
# # plt.xlabel("Time to download / Total time")
# # plt.savefig("download-percentage.png", bbox_inches='tight')
# # plt.close()
#
#
#
#
# tmp = 1
#
#
#
