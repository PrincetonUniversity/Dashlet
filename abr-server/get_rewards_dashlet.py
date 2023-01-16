import os
import json
import numpy as np
import argparse
import time
import csv
import xml.etree.ElementTree as ET
import re


folder = "/home/acer/Documents/ttstream/contentServer/dash/data/"

IDX_SEQ = 0
IDX_URI = 1
IDX_BITRATE = 3

class env:

    def _parseTime(self, path):
        tree = ET.parse(path + "/manifest.mpd")

        root = tree.getroot()

        field = root.attrib["mediaPresentationDuration"]
        num_str = re.sub("[^0-9.]", "", field)

        return float(num_str)

    def loadSwipe(self, tracename):
        swipe_percentage = np.loadtxt(tracename)

        nlen = min(len(swipe_percentage), len(self.swipe_trace))

        for i in range(nlen):
            self.swipe_trace[i][1] = self.swipe_trace[i][0] * swipe_percentage[i]

    def loadSequence(self, seqname):
        self.seq_map = {}
        self.swipe_trace = []
        self.maxbitrate_trace = []
        self.sequence = []


        row_cnt = 0
        with open(seqname, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:


                duration = self._parseTime(folder + row[IDX_URI])

                self.swipe_trace.append([duration, 0, int(row[IDX_SEQ])])

                bitrate_choices = row[IDX_BITRATE].split("&")
                max_bitrate = 0

                for item in bitrate_choices:
                    max_bitrate = max(max_bitrate, int(item))

                self.maxbitrate_trace.append(max_bitrate)

                if row[IDX_URI] not in self.seq_map.keys():
                    self.seq_map[row[IDX_URI]] = len(self.sequence)
                self.sequence.append(row[IDX_URI])


                row_cnt += 1

    def __init__(self, seqname, traceanme):
        self.loadSequence(seqname)
        self.loadSwipe(traceanme)


chunklength = 5.00

penalty_weight = 9193


# tracename = "../testing/dataclean/data/128.237.82.1-0.txt"
# seqname = "../testing/dataclean/vid.json"
# logname = "./out-empc-acc.log"
# outname = "./cooked-empcacc.log"

def cook_trace(swipetrace, playtrace, logname, outname, outname_best):

    e = env(playtrace, swipetrace)

    fd = open(logname, 'r')
    lines = fd.readlines()

    total_passed_time = 0
    total_download_time = 0

    total_download_size = 0

    buffer_map = {}
    for line in lines:
        items = line.split()

        buffer_map[(e.seq_map[items[1]], int(items[2]))] = (int(float(items[7])), float(items[5]))

        if e.seq_map[items[1]] < 80:
            total_download_time += float(items[5]) - float(items[4])
            total_passed_time = max(total_passed_time, float(items[5]))

            if e.seq_map[items[1]] != 0:
                total_download_size += int(float(items[7])) / 1000

    download_percentage = total_download_time / total_passed_time

    reward = 0

    vlen_arr = []

    video_time = 0

    chunk_rebuffering = []
    abr_history = []
    abr_best_history = []

    rebuffering_by_now = 0.0

    effect_download_size = 0



    for virtual_i in range(80):

        i = e.seq_map[e.sequence[virtual_i]]
        vlen = int((e.swipe_trace[i][1] - 0.000000001)/chunklength) + 1

        vlen_arr.append(vlen)

        for j in range(vlen):
            chunkfilesize = int(buffer_map[(i, j)][0] / 1000)

            chunk_time = min(chunklength, e.swipe_trace[i][0] - j * chunklength)
            view_time = min(chunklength, e.swipe_trace[i][1] - j * chunklength)

            reward += chunkfilesize * view_time / chunk_time

            if i != 0:
                effect_download_size += chunkfilesize * view_time / chunk_time

            downloadtime = buffer_map[(i, j)][1] / 1000

            abr_history.append((chunkfilesize * view_time / chunk_time, i))

            bitrate_max = e.maxbitrate_trace[i]

            abr_best_history.append((int(bitrate_max / 1000 / 8 * view_time), i))
            # abr_best_history.append()

            if (downloadtime - video_time - rebuffering_by_now > 0):
                chunk_rebuffering.append(downloadtime - video_time - rebuffering_by_now)
                rebuffering_by_now += downloadtime - video_time

            else:
                chunk_rebuffering.append(0.0)

            video_time += min(chunklength, e.swipe_trace[i][1] - chunklength * j)

    effect_percentage = effect_download_size / total_download_size


    fd = open(outname, "w")
    for i in range(len(chunk_rebuffering)):
        fd.write("%f %f %d\n" % (chunk_rebuffering[i], abr_history[i][0], abr_history[i][1]))
    fd.close()

    fd = open(outname_best, "w")
    for i in range(len(abr_best_history)):
        fd.write("%f %f %d\n" % (0, abr_best_history[i][0], abr_best_history[i][1]))
    fd.close()

    return download_percentage, effect_percentage


def main(args):

    # files = os.listdir(args.inputpath)

    download_percentage_list = []
    effect_percentage_list = []

    for network_idx in range(6, 20):
        network_tp = network_idx / 2.0

        for swipe_idx in range(2, 6):

            testname = f"trace-{network_tp:.1f}-swipe-{swipe_idx}"

            playtracepath = f"/home/acer/Documents/reverse-tiktok/data/{testname}/{testname}-play.csv"

            swipetracepath = f"/home/acer/Documents/reverse-tiktok/traces/swipe/swipe-{swipe_idx}.txt"

            loginname = f"{args.inputpath}{testname}.txt"
            logoutname = f"{args.dumppath}{testname}.txt"
            logoutname_best = f"{args.dumppath}{testname}-b.txt"

            download_percentage, effect_percentage = cook_trace(swipetracepath, playtracepath, loginname, logoutname, logoutname_best)

            download_percentage_list.append(download_percentage)
            effect_percentage_list.append(effect_percentage)

            # e = env(playtracepath, swipetracepath)


    fd = open("./results/effect-download-dashlet.txt", "w")
    for item in effect_percentage_list:
        fd.write(str(item))
        fd.write("\n")
    fd.close()


    fd = open("./results/download-percentage-dashlet.txt", "w")
    for item in download_percentage_list:
        fd.write(str(item))
        fd.write("\n")
    fd.close()

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dumppath', default='/home/acer/Documents/ttstream/run/cooked-sim/dashlet/', help='The path to save processed data')
    parser.add_argument('--inputpath', default='/home/acer/Documents/ttstream/run/result-sim/dashlet/', help='The path to get processed data')

    args = parser.parse_args()
    main(args)
