import os
import csv
import random

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import UnivariateSpline
import xml.etree.ElementTree as ET
import re

foldername = "../contentServer/dash/data/"

filenames = os.listdir(foldername)

def parseTimeFromManifest(path):
    tree = ET.parse(path + "/manifest.mpd")

    root = tree.getroot()

    field = root.attrib["mediaPresentationDuration"]
    num_str = re.sub("[^0-9.]", "", field)

    return float(num_str)


def sampling(lamba, time):

    nlen = int(time) + 1

    ret = [0 for i in range(nlen)]

    for i in range(nlen - 1):
        ret[i] = 0.9 * ((1 - np.exp(-1 * lamba * (i + 1) / time)) - (1 - np.exp(-1 * lamba * i / time)))

    ret[-1] = 1 - sum(ret)

    return ret


print(1-np.exp(-1 * 2))
print(1-np.exp(-1 * 3))
print(1-np.exp(-1 * 4))
print(1-np.exp(-1 * 5))


def get_bias_distribution(distribution, time, bias):

    bias_range = bias / 100 * time

    nlen = len(distribution)

    samples = [round(distribution[i] * 10000) for i in range(nlen)]

    output = [0 for i in range(nlen)]

    total = sum(samples[0:(nlen-1)])

    samples[-1] = 10000 - total

    for i in range(len(samples)):
        for j in range(samples[i]):
            val = i

            # val_min = max(i - bias_range, 0)
            # val_max = min(i + bias_range, time)

            val_rand = random.uniform(i+0.5 - bias_range, i +0.5 + bias_range)

            val_rand = max(val_rand, 0)
            val_rand = min(val_rand, time)

            idx = round(val_rand)

            if idx >= len(output):
                idx = len(output) - 1

            output[idx] += 1
    # print(sum(output))
    # tmp = 1


    for i in range(len(output)):
        output[i] /= 10000.0

    return output









def generate_biased_distribution(bias):
    foldername1 = f"./probability-bias/{bias}/"

    if os.path.exists(foldername1) == False:
        os.system(f"mkdir {foldername1}")

    for filename in filenames:
        if filename[0] == "v":
            time = parseTimeFromManifest(foldername+filename)

            for lamda in range(2, 6):
                foldername2 = f"./probability-bias/{bias}/lamda{lamda}/"

                if os.path.exists(foldername2) == False:
                    os.system(f"mkdir {foldername2}")

                distribution = sampling(lamda, time)

                distribution = get_bias_distribution(distribution, time, bias)

                fd = open(f"{foldername2}/{filename}.txt", "w")

                for i in range(len(distribution)):
                    fd.write(f"{distribution[i]:.10f}\n")

                fd.close()


bias_list = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
# bias_list = [25]
for bias in bias_list:
    generate_biased_distribution(bias)
    print(bias)

