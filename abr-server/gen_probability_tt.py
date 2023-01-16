import os
import csv
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

for filename in filenames:
    if filename[0] == "v":
        time = parseTimeFromManifest(foldername+filename)

        for lamda in range(2, 6):

            distribution = sampling(lamda, time)

            fd = open(f"./probability/lamda{lamda}/{filename}.txt", "w")

            for i in range(len(distribution)):
                fd.write(f"{distribution[i]:.10f}\n")

            fd.close()




