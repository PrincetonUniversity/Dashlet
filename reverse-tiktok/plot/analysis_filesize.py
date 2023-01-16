import csv
import numpy as np
import matplotlib.pyplot as plt
import random
from statsmodels.distributions.empirical_distribution import ECDF


def get_download_range(range_str):
    range_items = range_str.split()

    if len(range_items) == 1:
        return (0, 0)

    range_entries = range_items[1].split("/")

    range_values = range_entries[0].split("-")


    return (int(range_values[0]), int(range_values[1]))

def get_total_size(range_str):
    range_items = range_str.split()

    if len(range_items) == 1:
        return 0

    range_entries = range_items[1].split("/")

    return int(range_entries[1])


def load_network(filename):
    data = np.loadtxt(filename)

    ret = [0] * int(data[-1] / 1000 + 1)

    for i in range(len(data)):
        ret[int(data[i]/1000)] += 1

    for i in range(len(ret)):

        ret[i] = ret[i] * 1500 * 8 / 1000 / 1000

    return ret

IDX_DOWNLOAD_URI = 7
IDX_DOWNLOAD_RANGE = 1

IDX_REQUEST_START = 2
IDX_REQUEST_END = 3

IDX_RESPONSE_START = 4
IDX_RESPONSE_END = 5


norminal_bitrate = {"adapt_540_1": 851291, "lower_540_1": 558261, "lowest_540_1": 380301, "adapt_lower_720_1": 1081925}
quality_to_idx = {"adapt_lower_720_1": 3, "adapt_540_1": 2, "lower_540_1": 1, "lowest_540_1": 0, "normal_480_0": 2, "normal_540_1": 2, "lowest_540_0": 0, "lower_540_0": 0}

uri_to_norminal = {}
urireal_to_norminal = {}


def analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name):

    play_log = []
    download_log = []
    swipe_log = [0]


    uri_dict = {}

    uri_to_quality = {}
    uri_to_bitrate = {}



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
                    first_entries.append([float(row[IDX_RESPONSE_START]), float(row[IDX_RESPONSE_END]), downloadIdx, uri_to_quality[row[IDX_DOWNLOAD_URI]], float(row[IDX_REQUEST_START]), throughput_est, size_in_bytes, total_size_in_bytes, chunk_duration, uri_dict[row[IDX_DOWNLOAD_URI]], uri_to_bitrate[row[IDX_DOWNLOAD_URI]]])
                else:
                    second_entries.append([float(row[IDX_RESPONSE_START]), float(row[IDX_RESPONSE_END]), downloadIdx, uri_to_quality[row[IDX_DOWNLOAD_URI]], float(row[IDX_REQUEST_START]), throughput_est, size_in_bytes, total_size_in_bytes, chunk_duration, uri_dict[row[IDX_DOWNLOAD_URI]], uri_to_bitrate[row[IDX_DOWNLOAD_URI]]])

    return swipe_log, first_entries, second_entries

bitrate_throughput_all = []

bitrate_buffer_all = []
quality_dict_all = {}


throughput_s = []
bitrate_s = []
filesize_s = []
test_s = []

klen = [0]

for netid in range(8, 41):
    for swipeid in range(2, 6):

        foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
        play_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-play.csv"
        download_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-download.csv"
        swipe_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-swipe.log"

        print(foldername)

        swipe_log, first_entries, second_entries = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name)

        for i in range(1, len(first_entries)):
            # if first_entries[i][9][1] != (first_entries[i][9][2] - 1):

            if first_entries[i][9][1] != 0 and first_entries[i][9][1] != (first_entries[i][9][2] - 1):

                if first_entries[i][0] - first_entries[i-1][1] > 5:
                    continue

                throughput_s.append(first_entries[i-1][5])
                bitrate_s.append(first_entries[i][10])
                filesize_s.append(first_entries[i][7])

                test_s.append(first_entries[i])

        # break

    klen.append(len(throughput_s))
cnt = 0
for fs in filesize_s:
    if fs > 1024000:
       cnt += 1
print(cnt / len(filesize_s))
import scipy

throughput_s = np.array(throughput_s)
bitrate_s = np.array(bitrate_s)

slope, intercept, r, p, se = scipy.stats.linregress(throughput_s, bitrate_s)

idx = [i * 5 for i in range(400)]
idx = [i for i in range(2000)]


for test_idx in range(1, len(klen)):
    plt.figure()
    # plt.scatter([throughput_s[i] for i in idx], [bitrate_s[i] for i in idx])
    plt.scatter(throughput_s[0:klen[test_idx]], bitrate_s[0:klen[test_idx]])
    # plt.plot(throughput_s, intercept + slope*throughput_s, 'r', label='fitted line')


    plt.savefig(f"./dump/{test_idx}.png")

    plt.close()



