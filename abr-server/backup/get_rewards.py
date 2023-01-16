import os
import json
import numpy as np
import argparse
import time

class env:
    CHUNK_LENGTH = 5  # 5 seconds

    def loadSwipe(self, tracename):
        self.swipe_trace = np.loadtxt(tracename)

    def loadSequence(self, seqname):
        fd = open(seqname)
        self.seq_map = json.load(fd)
        fd.close()

        self.sequence = list(self.seq_map.keys())

    def __init__(self, seqname, traceanme):
        self.loadSwipe(traceanme)
        self.loadSequence(seqname)


bitraterewards = [1143, 2064, 4449, 6086, 9193, 0]
chunklength = 5.00

penalty_weight = 9193


# tracename = "../testing/dataclean/data/128.237.82.1-0.txt"
# seqname = "../testing/dataclean/vid.json"
# logname = "./out-empc-acc.log"
# outname = "./cooked-empcacc.log"

def cook_trace(tracename, seqname, logname, outname):

    e = env(seqname, tracename)

    fd = open(logname, 'r')
    lines = fd.readlines()

    buffer_map = {}
    for line in lines:
        items = line.split()

        buffer_map[(e.seq_map[items[1]], int(items[2]))] = (int(items[3]), float(items[5]))

    reward = 0

    vlen_arr = []

    video_time = 0

    chunk_rebuffering = []
    abr_history = []

    rebuffering_by_now = 0.0

    for i in range(20):
        vlen = int((e.swipe_trace[i][1] - 0.000000001)/chunklength) + 1

        vlen_arr.append(vlen)

        for j in range(vlen):
            bitrate = buffer_map[(i, j)][0]
            reward += bitraterewards[bitrate]

            downloadtime = buffer_map[(i, j)][1] / 1000

            abr_history.append(bitrate)

            if (downloadtime - video_time - rebuffering_by_now > 0):
                chunk_rebuffering.append(downloadtime - video_time - rebuffering_by_now)
                rebuffering_by_now += downloadtime - video_time

            else:

                chunk_rebuffering.append(0.0)

            video_time += min(chunklength, e.swipe_trace[i][1] - chunklength * j)


    fd = open(outname, "w")
    for i in range(len(chunk_rebuffering)):
        fd.write("%f %d\n" % (chunk_rebuffering[i], abr_history[i]))
    fd.close()


def main(args):

    cnt = 0
    # algorithm_list = ["empc", "mpc"]
    # algorithm_list = ["empc"]
    # probability_models = ["10timesaccurate", "byuser", "byvideo", "equal"]
    algorithm_list = ["oracle"]
    # probability_models = ["full_accuracy", "byuser", "byvideo", "equal"]
    probability_models = ["full_accuracy", "byvideo"]
    # network_traces = os.listdir(args.networktraces)[:2]
    network_traces = ["trace_9284_http---www.msn.com", "trace_10647_http---www.google.com-mobile-", "trace_6420_http---www.ebay.com", "trace_5357_http---www.ebay.com", "trace_5300_http---www.google.com-mobile-", "trace_28652_http---www.youtube.com", "trace_662422_http---edition.cnn.com", "trace_614990_http---www.google.com-mobile-"]
    viewing_traces = os.listdir(args.viewingtraces)

    for algorithm_iter in algorithm_list:

        foldername = f"{args.dumppath}/{algorithm_iter}"
        if os.path.exists(foldername) == False:
            os.system(f"mkdir {foldername}")

        for probability_iter in probability_models:

            foldername = f"{args.dumppath}/{algorithm_iter}/{probability_iter}"
            if os.path.exists(foldername) == False:
                os.system(f"mkdir {foldername}")

            for network_iter in network_traces:

                foldername = f"{args.dumppath}/{algorithm_iter}/{probability_iter}/{network_iter}"
                if os.path.exists(foldername) == False:
                    os.system(f"mkdir {foldername}")

                for viewing_iter in viewing_traces:

                    print(algorithm_iter, probability_iter, network_iter, viewing_iter)

                    tracename = f"{args.viewingtraces}/{viewing_iter}"
                    seqname = "../testing/dataclean/vid.json"
                    logname = f"{args.inputpath}/{algorithm_iter}/{probability_iter}/{network_iter}/{viewing_iter}"
                    outname = f"{args.dumppath}/{algorithm_iter}/{probability_iter}/{network_iter}/{viewing_iter}"

                    cook_trace(tracename, seqname, logname, outname)

    print(cnt)

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewingtraces', default='/home/acer/Documents/ttstream/testing/dataclean/data', help='Viewing trace path')
    parser.add_argument('--networktraces', default='/home/acer/Downloads/pensieve-master/traces/fcc/mahimahi', help='The id to sequence number mapping')
    parser.add_argument('--dumppath', default='/home/acer/Documents/ttstream/run/cooked-sim', help='The path to save processed data')
    parser.add_argument('--inputpath', default='/home/acer/Documents/ttstream/run/result-sim', help='The path to save processed data')

    args = parser.parse_args()
    main(args)
