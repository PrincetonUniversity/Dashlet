import csv
import numpy as np
import matplotlib.pyplot as plt
import random
from statsmodels.distributions.empirical_distribution import ECDF
import scipy.stats as st

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

    play_idx = 0


    max_download_chunk = 0

    download_progress = [(0, 0) for i in range(len(play_log))]

    throughput_all = []


    bitrate_buffer_list = []

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


                if ranges[0] != 1024000 and ranges[1] - ranges[0] != 0:
                    request_start_time = float(row[IDX_REQUEST_START])

                    while (play_idx + 1 < len(swipe_log) and swipe_log[play_idx + 1] < request_start_time):
                        play_idx += 1


                    if len(throughput_all) > 1:
                        print(len(throughput_all))
                        bitrate_buffer_list.append([bitrate_combo, downloadIdx - play_idx - 1, throughput_all[-1]])

                if ranges[1] - ranges[0] != 0:

                    this_size = (ranges[1] - ranges[0]) * 8

                    this_time = (float(row[IDX_RESPONSE_END]) - float(row[IDX_RESPONSE_START]))

                    this_throughput = this_size / 1000 / 1000 / this_time

                    # print(this_throughput)

                    throughput_all.append(this_throughput)
                else:
                    tmp = 1


    return bitrate_buffer_list


bitrate_buffer_all = []

for netid in range(6, 40):
    for swipeid in range(2, 6):
        foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
        play_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-play.csv"
        download_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-download.csv"
        swipe_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-swipe.log"

        print(foldername)

        bitrate_buffer_list = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name)

        bitrate_buffer_all.extend(bitrate_buffer_list)


buffers_bitrate_absolute = [[[] for i in range(8)] for j in range(5)]
buffers_bitrate_relative = [[[] for i in range(8)] for j in range(5)]


arrx = []
arry = []

for entry in bitrate_buffer_all:

    # if (entry[0][1] != 0 and entry[0][1] != entry[0][2]):
    # if (entry[0][1] == 0):
    arrx.append(entry[2])
    arry.append(entry[0][0])

    # bufferidx = entry[1]
slope, intercept, _, _, _ = st.linregress(arrx, arry)


print(slope)
slope = 93874.02577906292
print(intercept)
intercept = 150858.48070105485


plt.figure(figsize=(10, 10))

plt.plot([0, 20], [intercept, 20 * slope + intercept], "r")
plt.scatter(arrx, arry)
plt.xlim([0, 20])
plt.savefig("throughout_correlation.png")
plt.close()



