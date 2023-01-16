import os
import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import UnivariateSpline


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


for key in result_dict.keys():

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


        frequency_list = np.array(frequency_arr) * 0.9 + np.array([0.1 / len(frequency_arr) for i in range(len(frequency_arr))])

        fd = open(f"./probability/{key}.txt", "w")

        for i in range(len(frequency_list)):
            fd.write(f"{frequency_list[i]:.10f}\n")

        fd.close()

