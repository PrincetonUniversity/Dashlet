import csv
import numpy as np
import matplotlib.pyplot as plt
import random
from statsmodels.distributions.empirical_distribution import ECDF

plt.rcParams.update({'font.size': 18})

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



    with open(foldername+swipe_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            swipe_log.append(float(row[1]) - 0.1)



    with open(foldername+play_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            bitrates = row[3].split("&")

            encode_uri = row[4].split("&")
            parsed_row = [int(row[0]), row[1], int(row[2]), [int(bitrate) for bitrate in bitrates], encode_uri, row[5]]


            for i in range(len(encode_uri)):
                uri_dict[encode_uri[i]] = (int(row[0]), int(i/2), len(bitrates))

            play_log.append(parsed_row)
            # print(', '.join(row))


    # print(uri_dict.keys())



    play_idx = 0


    max_download_chunk = 0

    download_progress = [(0, 0) for i in range(len(play_log))]

    throughput_all = []


    bitrate_buffer_list = []
    bitrate_throughput_list = []

    buffer_list_play_end = []


    play_end_time_list = []
    request_finish_time_list = []
    request_start_time_list = []

    request_start_time_list_second = []


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



                # if len(throughput_all) > 1:
                #     bitrate_throughput_list.append([bitrate_combo, throughput_all[-1]])

                if ranges[0] != 1024000:

                    request_start_time = float(row[IDX_REQUEST_START])
                    request_start_time_list.append(request_start_time)
                    request_finish_time_list.append(float(row[IDX_REQUEST_END]))

                    while (play_idx + 1 < len(swipe_log) and swipe_log[play_idx + 1] < request_start_time):

                        play_idx += 1

                        play_end_time_list.append(swipe_log[play_idx])

                        buffer_list_play_end.append(downloadIdx - play_idx)


                    if len(throughput_all) > 1:
                        bitrate_buffer_list.append([bitrate_combo, downloadIdx - play_idx, throughput_all[-1]])
                    else:
                        bitrate_buffer_list.append([bitrate_combo, downloadIdx - play_idx, 0])

                if ranges[1] - ranges[0] != 0:

                    request_start_time_list_second.append(float(row[IDX_REQUEST_START]))

                    this_size = (ranges[1] - ranges[0]) * 8

                    this_time = (float(row[IDX_RESPONSE_END]) - float(row[IDX_RESPONSE_START]))

                    this_throughput = this_size / 1000 / 1000 / this_time

                    # print(this_throughput)

                    throughput_all.append(this_throughput)

                # download_metadata = uri_dict[row[IDX_DOWNLOAD_URI]]
                #
                # downloadIdx = download_metadata[0]
                #
                # request_start_time = float(row[IDX_DOWNLOAD_START])
                #
                # request_finish_time_list.append(request_start_time)
                #
                # while (play_idx + 1 < len(swipe_log) and swipe_log[play_idx + 1] < request_start_time):
                #     play_idx += 1
                #
                #
                # if ranges[0] == 1024000:
                #
                #     firstrequest = len(request_finish_time_list) - 1
                #
                #     while request_finish_time_list[firstrequest] > swipe_log[play_idx]:
                #         firstrequest -= 1
                #
                #     ret_second_chunk_time.append([play_idx, downloadIdx, (request_start_time - swipe_log[play_idx]), (max_download_chunk - play_idx), (len(request_finish_time_list) - 1 - firstrequest)])
                #
                # if ranges[0] == 1024000:
                #     download_progress[downloadIdx] = (2, 2)
                #
                # elif ranges[1] == 1024000:
                #     download_progress[downloadIdx] = (1, 2)
                #
                # else:
                #     download_progress[downloadIdx] = (1, 1)
                #
                # max_download_chunk = max(max_download_chunk, downloadIdx)


    # play_end_time_list = []
    # request_finish_time_list = []

    arr = [0] * 7700

    offest = request_finish_time_list[0] - 10


    for i in range(len(request_start_time_list)):
        request_start_time_list[i] -= offest

    for i in range(len(request_start_time_list_second)):
        request_start_time_list_second[i] -= offest

    for i in range(len(request_finish_time_list)):

        idx = int((request_finish_time_list[i] - offest) * 10)

        for j in range(idx, 7700):
            arr[j] += 1

    for j in range(105, 7700):
        arr[j] -= 1

    for i in range(len(play_end_time_list)):
        idx = int((play_end_time_list[i] - offest) * 10)

        for j in range(idx, 7700):
            arr[j] -= 1

    plt.plot(arr)
    plt.show()

    np.savetxt("buffer_time_low.txt", arr, fmt="%d")

    np.savetxt("first_request_time_low.txt", request_start_time_list, fmt="%4.6f")
    np.savetxt("second_request_time_low.txt", request_start_time_list_second, fmt="%4.6f")
    # np.savetxt("play_finish_time.txt", play_end_time_list, fmt="%4.6f")

    return bitrate_throughput_list, bitrate_buffer_list, buffer_list_play_end


bitrate_throughput_all = []

bitrate_buffer_all = []

buffer_list_play_end = []

for netid in range(6, 7):
    for swipeid in range(2, 3):
        foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
        play_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-play.csv"
        download_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-download.csv"
        swipe_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-swipe.log"

        print(foldername)

        bitrate_throughput_list, bitrate_buffer_list, buffer_list_play_end = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name)

        bitrate_throughput_all.extend(bitrate_throughput_list)
        bitrate_buffer_all.extend(bitrate_buffer_list)

arr = []
arr2 = []

plt.figure(figsize=(6,3))

for i in range(80):
    arr.extend([bitrate_buffer_all[i][1] for j in range(1)])

    arr2.extend([buffer_list_play_end[i] for j in range(1)])



np.savetxt("download_start_low.txt", arr, fmt='%d')
np.savetxt("play_finish.txt", arr2, fmt='%d')


plt.plot([0.01 * i for i in range(len(arr))], arr, LineWidth=3)

plt.plot([0.01 * i for i in range(len(arr2))], arr2, LineWidth=3, linestyle="--")


for i in range(1, 9):

    plt.plot([i*10, i*10], [0, 5], color="grey", linestyle="--")



plt.xlabel("Video index")
plt.ylabel("#Buffered videos")


# plt.legend()
# plt.grid()
plt.savefig("TikTok-buffer-dynamics.pdf", bbox_inches="tight")
plt.close()

# plt.show()
# plt.close()