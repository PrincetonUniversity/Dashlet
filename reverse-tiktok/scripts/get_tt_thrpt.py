import csv

import numpy as np

IDX_DOWNLOAD_URI = 7
IDX_DOWNLOAD_RANGE = 1

IDX_REQUEST_START = 2
IDX_REQUEST_END = 3

IDX_RESPONSE_START = 4
IDX_RESPONSE_END = 5


def get_download_range(range_str):
    range_items = range_str.split()

    if len(range_items) == 1:
        return (0, 0)

    range_entries = range_items[1].split("/")

    range_values = range_entries[0].split("-")


    return (int(range_values[0]), int(range_values[1]))


def parse_download_log(foldername, download_log_name):
    throughput_individual = []
    data_all = 0.0
    time_all = 0.0
    with open(foldername+download_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            ranges = get_download_range(row[IDX_DOWNLOAD_RANGE])

            download_time = float(row[IDX_RESPONSE_END]) - float(row[IDX_REQUEST_START])

            if ranges[1] - ranges[0] != 0:

                throughput_individual.append((ranges[1] - ranges[0]) * 8 / 1000 / 1000 / download_time)

                data_all += (ranges[1] - ranges[0]) * 8 / 1000 / 1000
                time_all += download_time

    # print(np.average(throughput_individual))
    # print(data_all / time_all)

    return np.average(throughput_individual), data_all / time_all

throughput_list = []


for netid in range(6, 11):
    for swipeid in range(2, 5):

        foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
        download_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-download.csv"

        print(f"=============== {netid/2:.1f} ===============")

        throughput_1, throughput_2 = parse_download_log(foldername, download_log_name)

        throughput_list.append(throughput_1 / (netid/2))

print(throughput_list)
print(np.average(throughput_list))





