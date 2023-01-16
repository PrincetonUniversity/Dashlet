import os
import csv
import matplotlib.pyplot as plt
import numpy as np

foldername = "/home/acer/Downloads/mturk-code/createhit/gooddata/"
filenames = os.listdir(foldername)

result_dict = {}

for filename in filenames:
    with open(foldername+filename, newline='') as csvfile:
        print(filename)
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if row[2] == 'NaN':
                continue
            if row[0] == 'countdown':
                continue

            if row[0] not in result_dict.keys():
                result_dict[row[0]] = []

            result_dict[row[0]].append(row)

name_to_idx = {"5904810145583287557": 0, "5925559746128907526": 1, "5925850612991151365": 2, "5926975697558850821": 3}

klist = [[] for i in range(4)]

for key in name_to_idx.keys():

    if len(result_dict[key]) > 10:

        data_arr = []

        frequency_arr = [0] * (int(float(result_dict[key][0][2]) / 1.0) + 1)

        for i in range(len(result_dict[key])):
            data_arr.append(float(result_dict[key][i][1]))

        for i in range(len(data_arr)):

            idx = int(data_arr[i] / 1.0)

            if idx >= len(frequency_arr):
                frequency_arr[-1] += 1 / len(data_arr)
            else:
                frequency_arr[idx] += 1 / len(data_arr)


        klist[name_to_idx[key]] = frequency_arr

result = [np.array([]) for i in range(4)]
result[0] = np.array(klist[0])

for i in range(1, 4):
    result[i] = np.convolve(result[i-1], klist[i])


for i in range(4):
    x = [i + 1 for i in range(len(result[i]))]
    plt.bar(x, result[i])

    plt.ylabel("Watch start time (s)")
    plt.xlabel("Probability distribution")
    plt.xlim([0, 120])
    plt.savefig(f"./distribution/{i}.png", bbox_inches='tight')


tmp = 1

        # x = [i + 1 for i in range(len(frequency_arr))]
        # plt.bar(x, frequency_arr)
        #
        # plt.ylabel("viewing cnt")
        # plt.xlabel("chunk index")
        # # plt.savefig(f"./distribution/{key}.png", bbox_inches='tight')
        #
        # plt.show()
        #
        # plt.close()

# for key in result_dict.keys():
#
#     if len(result_dict[key]) > 10:
#
#         data_arr = []
#
#         frequency_arr = [0] * (int(float(result_dict[key][0][2]) / 1.0) + 1)
#
#         for i in range(len(result_dict[key])):
#             data_arr.append(float(result_dict[key][i][1]))
#
#         for i in range(len(data_arr)):
#
#             idx = int(data_arr[i] / 1.0)
#
#             if idx >= len(frequency_arr):
#                 frequency_arr[-1] += 1
#             else:
#                 frequency_arr[idx] += 1
#
#
#         x = [i + 1 for i in range(len(frequency_arr))]
#         plt.bar(x, frequency_arr)
#
#         plt.ylabel("viewing cnt")
#         plt.xlabel("chunk index")
#         # plt.savefig(f"./distribution/{key}.png", bbox_inches='tight')
#
#         plt.show()
#
#         plt.close()


