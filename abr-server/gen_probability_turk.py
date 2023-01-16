import os
import csv
from scipy import stats

import matplotlib.pyplot as plt

import numpy as np


foldername = "/home/acer/Downloads/mturk-code/createhit/gooddata/"
filenames = os.listdir(foldername)

result_dict = {}

for filename in filenames:
    with open(foldername+filename, newline='') as csvfile:
        # print(filename)
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if row[2] == 'NaN':
                continue
            if row[0] == 'countdown':
                continue

            if row[0] not in result_dict.keys():
                result_dict[row[0]] = []

            result_dict[row[0]].append(float(row[1]))

files = os.listdir("/home/acer/Documents/reverse-tiktok/video-buffer/")

ofiles = []

for file in files:
    if file[0] == "v" and file[-1] == "4":
        fnamet = file.strip(".mp4")

        ofiles.append(fnamet)

def getDensity(data):
    mval = max(data)
    fitdata = []

    for i in range(len(data)):
        if abs(mval - data[i]) > 0.001:
            fitdata.append(data[i])

    kde = stats.gaussian_kde(fitdata)
    x = np.linspace(0, int(mval), int(mval) + 1)
    p = kde(x)

    p = p / np.sum(p) * len(fitdata) / len(data)

    p[int(mval)] = 1 - (np.sum(p) - p[int(mval)])

    return p

out_dict = {}
out_dict["v12044gd0000cc6o2grc77ud2dph6slg"] = np.ones(12) / 12.0
out_dict["v12044gd0000cc6kedbc77u1qf58odk0"] = np.ones(9) / 9.0

for vname in ofiles:
    if vname in result_dict.keys():
        distribution = result_dict[vname]
        dis = getDensity(distribution)

        out_file_name = f"./probability/turk/{vname}.txt"
        np.savetxt(out_file_name, dis, fmt='%1.10f')
    else:
        out_file_name = f"./probability/turk/{vname}.txt"
        np.savetxt(out_file_name, out_dict[vname], fmt='%1.10f')

        # print(np.sum(dis))
        # tmp = 1