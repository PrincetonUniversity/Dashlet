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


IDX_DOWNLOAD_URI = 7
IDX_DOWNLOAD_RANGE = 1

IDX_REQUEST_START = 2
IDX_REQUEST_END = 3

IDX_RESPONSE_START = 4
IDX_RESPONSE_END = 5


norminal_bitrate = {"adapt_540_1": 851291, "lower_540_1": 558261, "lowest_540_1": 380301, "adapt_lower_720_1": 1081925}


def analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name):

    play_log = []
    download_log = []
    swipe_log = [0]


    uri_dict = {}

    quality_dict = {}



    with open(foldername+swipe_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            swipe_log.append(float(row[1]))



    with open(foldername+play_log_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            bitrates = row[3].split("&")

            encode_uri = row[4].split("&")

            bitrate_names = row[6].split("&")
            qualitysettings = row[7].split("&")



            parsed_row = [int(row[0]), row[1], int(row[2]), [int(bitrate) for bitrate in bitrates], encode_uri, row[5], bitrate_names, qualitysettings]

            for i in range(len(bitrate_names)):
                if (bitrate_names[i], qualitysettings[i]) not in quality_dict.keys():
                    quality_dict[(bitrate_names[i], qualitysettings[i])] = []

                quality_dict[(bitrate_names[i], qualitysettings[i])].append(int(bitrates[i]))

            for i in range(len(encode_uri)):
                uri_dict[encode_uri[i]] = (int(row[0]), int(i/2), len(bitrates))


            play_log.append(parsed_row)
            # print(', '.join(row))


    # print(quality_dict.keys())



    play_idx = 0


    max_download_chunk = 0

    download_progress = [(0, 0) for i in range(len(play_log))]

    throughput_all = []


    bitrate_buffer_list = []
    bitrate_throughput_list = []


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

                quality_string = play_log[downloadIdx][6][bitrateIdx]

                if quality_string in norminal_bitrate.keys():
                    bitrate_decision = norminal_bitrate[quality_string]



                bitrate_combo = (bitrate_decision, download_metadata[1], download_metadata[2] - 1)



                # if len(throughput_all) > 1:
                #     bitrate_throughput_list.append([bitrate_combo, throughput_all[-1]])






                if ranges[0] != 1024000:
                    request_start_time = float(row[IDX_REQUEST_START])

                    while (play_idx + 1 < len(swipe_log) and swipe_log[play_idx + 1] < request_start_time):
                        play_idx += 1


                    if len(throughput_all) > 1:
                        bitrate_buffer_list.append([bitrate_combo, downloadIdx - play_idx, throughput_all[-1]])

                tmp = 1



                if ranges[1] - ranges[0] != 0:

                    this_size = (ranges[1] - ranges[0]) * 8

                    this_time = (float(row[IDX_RESPONSE_END]) - float(row[IDX_RESPONSE_START]))

                    this_throughput = this_size / 1000 / 1000 / this_time

                    print(this_throughput)

                    throughput_all.append(this_throughput)

                # download_metadata = uri_dict[row[IDX_DOWNLOAD_URI]]
                #
                # downloadIdx = download_metadata[0]
                #
                # request_start_time = float(row[IDX_DOWNLOAD_START])
                #
                # request_start_time_list.append(request_start_time)
                #
                # while (play_idx + 1 < len(swipe_log) and swipe_log[play_idx + 1] < request_start_time):
                #     play_idx += 1
                #
                #
                # if ranges[0] == 1024000:
                #
                #     firstrequest = len(request_start_time_list) - 1
                #
                #     while request_start_time_list[firstrequest] > swipe_log[play_idx]:
                #         firstrequest -= 1
                #
                #     ret_second_chunk_time.append([play_idx, downloadIdx, (request_start_time - swipe_log[play_idx]), (max_download_chunk - play_idx), (len(request_start_time_list) - 1 - firstrequest)])
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

    return bitrate_throughput_list, bitrate_buffer_list, quality_dict






bitrate_throughput_all = []

bitrate_buffer_all = []
quality_dict_all = {}


for netid in [0, 1, 2, 3, 4, 10, 11, 12]:
    for swipeid in range(2, 7):
        foldername = f"../data/ifi-{netid}-swipe-{swipeid}/"
        play_log_name = f"ifi-{netid}-swipe-{swipeid}-play.csv"
        download_log_name = f"ifi-{netid}-swipe-{swipeid}-download.csv"
        swipe_log_name = f"ifi-{netid}-swipe-{swipeid}-swipe.log"

        print(foldername)

        bitrate_throughput_list, bitrate_buffer_list, quality_dict = analysis_entry(foldername, play_log_name, download_log_name, swipe_log_name)

        for key in quality_dict.keys():
            if key not in quality_dict_all:
                quality_dict_all[key] = []

            quality_dict_all[key].extend(quality_dict[key])

        bitrate_throughput_all.extend(bitrate_throughput_list)
        bitrate_buffer_all.extend(bitrate_buffer_list)

for key in quality_dict_all.keys():
    print(key[0])
    print(np.average(quality_dict_all[key]))

print(len(bitrate_throughput_all))
print(len(bitrate_buffer_all))


# throughput_x = []
# bitrate_y = []

# random.seed(0)
# random.shuffle(bitrate_throughput_all)

# heat_map = [[1 for i in range(15)] for j in range(11)]

# for entry in bitrate_throughput_all:

#     this_bitrate = 0
#     if entry[0][2] != 0:
#         this_bitrate = entry[0][1] / entry[0][2]

#     this_thropughput = entry[1]

#     throughput_x.append(this_thropughput)
#     bitrate_y.append(this_bitrate)

#     if this_thropughput < 15 and entry[0][2] != 0:
#         heat_map_x = int(this_thropughput)

#         heat_map_y = int(this_bitrate / 0.1)

#         heat_map[heat_map_y][heat_map_x] += 1


# plt.figure()
# ax = plt.imshow(heat_map)
# # ax.invert_yaxis()

# plt.gca().invert_yaxis()

# plt.xlabel("Throughput (Mbps)")
# plt.ylabel("Video Bitrate Index")

# # plt.xlim([0, 25])
# plt.savefig("Throughput_bitrate.png", bbox_inches='tight')

# plt.close()



# throughput_x = []
# bitrate_y = []
#
# random.seed(0)
# random.shuffle(bitrate_throughput_all)
#
# heat_map = [[1 for i in range(15)] for j in range(10)]
#
# for entry in bitrate_throughput_all:
#
#
#     this_thropughput = entry[1]
#     this_bitrate = entry[0][0]
#     throughput_x.append(this_thropughput)
#     bitrate_y.append(this_bitrate)
#
#     if this_thropughput < 15 and this_bitrate < 1000000:
#         heat_map_x = int(this_thropughput)
#
#         heat_map_y = int(this_bitrate/ 100000)
#
#         heat_map[heat_map_y][heat_map_x] += 1
#
#
# plt.figure()
# ax = plt.imshow(heat_map)
# # ax.invert_yaxis()
#
# plt.gca().invert_yaxis()
#
# plt.xlabel("Throughput (Mbps)")
# plt.ylabel("Video Bitrate x 10^5 bps")
#
# # plt.xlim([0, 25])
# plt.savefig("Throughput_bitrate.png", bbox_inches='tight')
#
# plt.close()


tmp = 1

# plt.figure()
# plt.scatter(throughput_x, bitrate_y)
# plt.xlabel("Throughput (Mbps)")
# plt.ylabel("Bitrate")
#
# plt.xlim([0, 25])
# plt.savefig("Throughput_bitrate.png", bbox_inches='tight')
#
# plt.close()





####################

buffers_bitrate_absolute = [[[] for i in range(8)] for j in range(7)]
buffers_bitrate_relative = [[[] for i in range(8)] for j in range(7)]

buffer_invalid = 0
throughput_invalid = 0

for entry in bitrate_buffer_all:

    bufferidx = entry[1]

    if bufferidx >= 9:
        bufferidx -= 10

    # rebuffering
    if bufferidx < 0:
        bufferidx = -1



    if bufferidx > 5:
        print(bufferidx)
        buffer_invalid += 1
        continue

    if entry[2] >= 16:
        throughput_invalid += 1
        continue

    netidx = int(entry[2] / 2)

    tmp = 1
    buffers_bitrate_absolute[(bufferidx + 1) % 7][netidx].append(entry[0][0] / 1000)

    if entry[0][2] == 0:
        # buffers_bitrate_relative[(bufferidx + 1) % 7][netidx].append(0)
        tmp = 1

    else:
        buffers_bitrate_relative[(bufferidx + 1) % 7][netidx].append(entry[0][1] / entry[0][2])


table_absolute = np.array([[0.0 for i in range(8)] for j in range(7)])
table_relative = np.array([[0.0 for i in range(8)] for j in range(7)])


for i in range(7):
    for j in range(8):
        if len(buffers_bitrate_absolute[i][j]) > 10:
            table_absolute[i][j] = np.average(buffers_bitrate_absolute[i][j])
        else:
            table_absolute[i][j] = np.nan


        if len(buffers_bitrate_relative[i][j]) > 10:
            table_relative[i][j] = np.average(buffers_bitrate_relative[i][j])
        else:
            table_relative[i][j] = np.nan

# table_absolute[table_absolute == 0.0] = np.nan


plt.figure()
ax = plt.imshow(table_absolute)

plt.gca().invert_yaxis()

plt.xlabel("Throughput (Mbps)")
plt.ylabel("# of buffered video")
plt.xticks([0, 1, 2, 3, 4, 5, 6, 7], [2, 4, 6, 8, 10, 12, 14, 16])
plt.yticks([0, 1, 2, 3, 4, 5, 6], ["rebuffer", "0", "1", "2", "3", "4", "5"])
bar = plt.colorbar(ax)
plt.savefig("Throughput_bitrate_absolute.png", bbox_inches='tight')
plt.close()

tmp = 1


plt.figure()
ax = plt.imshow(table_relative)
plt.gca().invert_yaxis()
plt.xlabel("Throughput (Mbps)")
plt.ylabel("# of buffered video")
plt.xticks([0, 1, 2, 3, 4, 5, 6, 7], [2, 4, 6, 8, 10, 12, 14, 16])
plt.yticks([0, 1, 2, 3, 4, 5, 6], ["rebuffer", "0", "1", "2", "3", "4", "5"])
bar = plt.colorbar(ax)
plt.savefig("Throughput_bitrate_relative.png", bbox_inches='tight')
plt.close()


plt.figure(figsize=(28*2, 32*2), dpi=300)
fig, axs = plt.subplots(7, 8)


ylabs = ["rebuffer", "0", "1", "2", "3", "4", "5"]
xlabs = ["2", "4", "6", "8", "10", "12", "14", "16Mbps"]

for i in range(7):
    for j in range(8):

        if len(buffers_bitrate_absolute[i][j]) > 15:

            ecdf1 = ECDF(buffers_bitrate_absolute[i][j])
            axs[i, j].plot(ecdf1.x, ecdf1.y)


            axs[i, j].set_xticks([0, 250, 500, 750, 1000])
            axs[i, j].set_yticks([0, 0.250, 0.500, 0.750, 1.0])



            axs[i, j].set_yticklabels([])

            axs[i, j].grid(True)

            axs[i, j].set_xlim(0, 1000)

            if i == 6 and j == 0:
                tmp = 1
                axs[i, j].set_yticklabels(["0", "", "", "", "1"])
                axs[i, j].set_xticklabels(["0", "", "", "", "1000"])
                axs[i, j].set_xlabel("video bitrate (Kbps)")
                # axs[i, j].set_ylabel("CDF")
            else:
                axs[i, j].set_xticklabels([])
                # axs[i, j].get_xaxis().set_ticks([])



        else:
            axs[i, j].axis('off')


        if j == 0:
            axs[i, j].set_ylabel(ylabs[i])
            # axs[i, j].get_yaxis().set_ticks([0, 0.5, 1.0], ["", "", ""])
        else:
            tmp = 1
            # axs[i, j].get_yaxis().set_ticks([])

        if i == 0:
            axs[i, j].set_title(xlabs[j])




plt.savefig("abusolute_cdf.png", bbox_inches='tight', dpi=600)

plt.close()



        # axs[i, j].plot(x, y)
# axs[0, 0].set_title('Axis [0, 0]')
# axs[0, 1].plot(x, y, 'tab:orange')
# axs[0, 1].set_title('Axis [0, 1]')
# axs[1, 0].plot(x, -y, 'tab:green')
# axs[1, 0].set_title('Axis [1, 0]')
# axs[1, 1].plot(x, -y, 'tab:red')
# axs[1, 1].set_title('Axis [1, 1]')

# print(len(buffers_bitrate_absolute[-1]))


# print(buffers_bitrate_absolute[-1])
# for i in range(6):
#     buffers_bitrate_absolute_mean.append(np.average(buffers_bitrate_absolute[i]))
#
#     # print(len(buffers_bitrate_absolute[i]))
#
#
#
#
# buffers_bitrate_relative_mean = []
#
# buffers_bitrate_relative_mean.append(np.average(buffers_bitrate_relative[-1]))
#
# for i in range(7):
#     buffers_bitrate_relative_mean.append(np.average(buffers_bitrate_relative[i]))
#
#
# plt.figure()
# plt.plot([i for i in range(-1, 6)], buffers_bitrate_relative_mean[0:7])
# plt.xlabel("Prebuffered videos")
# plt.ylabel("Average Relative bitrate index")
# plt.ylim([0, 1.0])
# plt.savefig("buffers_bitrate_relative.png", bbox_inches='tight')
# plt.close()
#
#
# plt.figure()
# plt.plot([i for i in range(-1, 6)], buffers_bitrate_absolute_mean[0:7])
# plt.xlabel("Prebuffered videos")
# plt.ylabel("Average bitrate")
# plt.ylim([0, 800000])
# plt.savefig("buffers_bitrate_absolute.png", bbox_inches='tight')
# plt.close()








