#!/usr/bin/env python
import copy

from http.server import BaseHTTPRequestHandler, HTTPServer
# import SocketServer
import base64
import urllib
import sys
import os
import json
import argparse
import time
import csv
import numpy as np
import xml.etree.ElementTree as ET
import re

from abrAlgorithmCollection import mpc_sv, prob_tree_sv, prob_tree_sv_short, prob_mpc
os.environ['CUDA_VISIBLE_DEVICES']=''

import time

LOG_FILE = './results/log'

buffer_test = [
    # [0, -2, -2, -2, -2],
    # [1, -2, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [-2, 0, -2, -2, -2],
    # [3, -2, -2, -2, -2],
    # [4, -2, -2, -2, -2],
    # [-2, 0, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [-2, 0, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [-2, 0, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [-2, -2, 4, -2, -2],
    # [4, -2, -2, -2, -2],
    # [1, -2, -2, -2, -2],
    # [1, -2, -2, -2, -2],
    # [3, -2, -2, -2, -2],
    # [4, -2, -2, -2, -2],
    # [-2, -2, 4, -2, -2],
    # [-2, 4, -2, -2, -2],
    # [-2, 0, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [-2, 1, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [-2, 0, -2, -2, -2],
    # [-2, 0, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [0, -2, -2, -2, -2],
    # [-2, 0, -2, -2, -2],
    # [1, -2, -2, -2, -2],
    # [-2, -2, 4, -2, -2],
    # [1, -2, -2, -2, -2],
    # [-2, -2, 4, -2, -2],
    # [2, -2, -2, -2, -2],
    # [2, -2, -2, -2, -2],
    # [-2, -2, -2, 4, -2],
]

# swipe_map = {"5904810145583287557": 2, "5925559746128907526": 1, "5925850612991151365": 3, "5926975697558850821": 7, "5927147240498793733": 1, "6836783718552636678": 1, "6836801837312576774": 1, "6836860558994590981": 2, "6837206354168417541": 1, "6837216137567079685": 0, "6837275422036610310": 0, "6837292828096285954": 0, "6837297918941220101": 2, "6837522748605025541": 1, "6837729565700328710": 1, "6837993705631239430": 1, "6838617182075636997": 1, "6838639492379708678": 2, "6838657148331805958": 0, "6838698072097295621": 3, "6839442908559543557": 0, "6839503838181936389": 3, "6839758048060378373": 0, "6839767741440806150": 1, "6839852501768883462": 2, "6839879071011228934": 1, "6839882323178081542": 0, "6840232264199048454": 1, "6840361628588870917": 0, "6840420887305538821": 0}

probability_map = {}


IDX_TOTAL_DURATION = 2
IDX_URI = 1

folder = "/home/acer/Documents/ttstream/contentServer/dash/data/"


def _parseTime(path):
    tree = ET.parse(path + "/manifest.mpd")

    root = tree.getroot()

    field = root.attrib["mediaPresentationDuration"]
    num_str = re.sub("[^0-9.]", "", field)

    return float(num_str)


def cdf(lamda, x):
    return 1 - np.exp(-1 * lamda * x)

def get_probability_map(tracename, lamda):
    probability_map_f = {}

    with open(tracename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            # print(row)

            duration = _parseTime(folder + row[IDX_URI])
                # float(row[IDX_TOTAL_DURATION]) / 1000

            probability_map_f[row[IDX_URI]] = []

            nlen = int(duration / 5.0)

            if abs(nlen * 5.0 - duration) > 0.0001:
                nlen += 1

            total_prob = 1.0

            for i in range(nlen - 1):

                start = i * 5.0 / duration
                end = (i + 1) * 5.0 / duration

                val = (cdf(lamda, end) - cdf(lamda, start)) * 0.9

                total_prob -= val

                probability_map_f[row[IDX_URI]].append(val)

            probability_map_f[row[IDX_URI]].append(total_prob)







            # self.seq_map[row[IDX_URI]] = int(row[IDX_SEQ])
            # 
            # self.swipe_trace.append([float(row[IDX_TOTAL_DURATION]) / 1000, 0, int(row[IDX_SEQ])])

    # with open(tracename) as f:
    #     lines = f.read().splitlines()
    #
    #     for line in lines:
    #         items = line.split()
    #
    #         probability_map_f[items[0]] = []
    #
    #         for i in range(1, len(items)):
    #             probability_map_f[items[0]].append(float(items[i]))

    return probability_map_f


bitrate_folder = "/home/acer/Documents/ttstream/contentServer/dash/data/"

def parse_vid(url):
    return url.split("/")[5]

def get_probability_weights(events):
    # print(events)

    total_lengths = [int(event["duration"] / 5.0) + 1 for event in events]

    probability_weights = []
    for i in range(len(total_lengths)):
        vid = parse_vid(events[i]['url'])
        probability_weights.append(probability_map[vid])

    return probability_weights


"""
Theoretically the bitrate profile for each chunk should be obtained from the 
manifest file, we directly get in from the file for this batch of implementation 
for simplicity since it is not in the core design of short video streaming algorithm 
"""
def get_bitrate(events):
    bitrate_list = []

    for eidx, event in enumerate(events):
        bitrate_list.append([])
        uid = parse_vid(event['url'])
        path = bitrate_folder + uid

        nfiles = len(os.listdir(path))

        nseg = (nfiles // 6) - 1

        duration = event['duration']

        nseg = int(duration / 5.0)

        if abs(duration - nseg * 5.0) > 0.00001:
            nseg += 1

        for i in range(nseg):

            bitrate_list[eidx].append([])

            a_size = os.path.getsize(path + "/chunk-stream5-%05d.m4s" % (i + 1))

            for j in range(5):
                v_size = os.path.getsize(
                    path + """/chunk-stream%d-%05d.m4s""" % (j, (i + 1))
                )

                bitrate_list[eidx][i].append((v_size + a_size) * 8 / 1000.0) # in kb
                # self.vsize[i].append(v_size)
    return bitrate_list


class ThroughputEstimator:
    def __init__(self):
        self.throughput_history = []
        self.throughput_events = {}

    def append_throughput(self, event):
        vid = parse_vid(event['url'])
        if vid not in self.throughput_events.keys():
            self.throughput_events[vid] = []
        else:
            if event['lastRequest'] == len(self.throughput_events[vid]):
                self.throughput_events[vid].append(event['bandwidthEst'])
                self.throughput_history.append(event['bandwidthEst'])

            elif event['lastRequest'] + 1 > len(self.throughput_events[vid]):
                print("error happens in append_download")
            # do nothing when the data is already logged

    def get_throughput_est(self):
        # return a low throughput to have a fast start
        if len(self.throughput_history) == 0:
            return 100

        history_len = len(self.throughput_history)

        history_end = history_len

        history_start = max(history_len - 5, 0)

        window_len = history_end - history_start

        reverse_sum = 0

        for i in range(history_start, history_end):
            reverse_sum += (1.0 / self.throughput_history[i])

        return window_len / reverse_sum


class DataLogger:
    def __init__(self, path):
        self.path = path

        self.download_events = {}
        self.swipe_events = {}


    def open(self):
        self.fd = open(self.path, "w")


    def close(self):
        self.fd.close()


    def append_swipe(self, event):
        # print(event)

        vid = parse_vid(event['url'])

        self.fd.write("[swipe]" + '\t' +
                      vid + '\t' +
                      str(event['swipeTime']) + '\t' +
                      str(event['viewTime']) + '\n')
        self.fd.flush()


    def append_download(self, event):
        vid = parse_vid(event['url'])
        if vid not in self.download_events.keys():
            self.download_events[vid] = []
        else:
            if event['lastRequest'] == len(self.download_events[vid]):

                # print("[download]" + '\t' +
                #       vid + '\t' +
                #       str(event['lastRequest']) + '\t' +
                #       str(event['lastquality']) + '\t' +
                #       str(event['lastChunkStartTime']) + '\t' +
                #       str(event['lastChunkFinishTime']) + '\t' +
                #       str(event['duration']))

                self.fd.write("[download]" + '\t' +
                              vid + '\t' +
                              str(event['lastRequest']) + '\t' +
                              str(event['lastquality']) + '\t' +
                              str(event['lastChunkStartTime']) + '\t' +
                              str(event['lastChunkFinishTime']) + '\t' +
                              str(event['duration']) + '\n')
                self.fd.flush()

                self.download_events[vid].append([event['lastquality'],
                                                  event['lastChunkStartTime'],
                                                  event['lastChunkFinishTime'],
                                                  event['duration']])

            elif event['lastRequest'] + 1 > len(self.download_events[vid]):
                print("error happens in append_download")
            # do nothing when the data is already logged

def make_request_handler(input_dict, logger, throughput_estimator):

    class Request_Handler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.input_dict = input_dict
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        def do_POST(self):

            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))

            if post_data["isinfo"] == -1:

                send_data= b"-2"
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', len(send_data))
                self.send_header('Access-Control-Allow-Origin', "*")
                self.end_headers()
                self.wfile.write(send_data)

                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)

            # print(post_data)
            if post_data["isinfo"] == 1:
                # print("info")
                input_dict["info_phase"] = True

                idx = post_data['playerId'] - post_data['currentPlayerIdx']

                if idx < 0:
                    idx += 5

                input_dict["events_record"][idx] = copy.deepcopy(post_data)

                logger.append_download(post_data)
                throughput_estimator.append_throughput(post_data)

                # print(input_dict["events_record"])

                send_data= b"-2"
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', len(send_data))
                self.send_header('Access-Control-Allow-Origin', "*")
                self.end_headers()
                self.wfile.write(send_data)

                # return
            else:

                # print(post_data)
                if post_data['Type'] == 'swipe':
                    logger.append_swipe(post_data)

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.send_header('Content-Length', 0)
                    self.send_header('Access-Control-Allow-Origin', "*")
                    self.end_headers()

                else:
                    if input_dict["info_phase"] == True:
                        probability_weights = get_probability_weights(input_dict["events_record"])
                        bitrate = get_bitrate(input_dict["events_record"])

                        if self.input_dict["ITER_CNT"] < len(buffer_test):
                            input_dict["buffer_plan"] = buffer_test[self.input_dict["ITER_CNT"]]
                            print(buffer_test[self.input_dict["ITER_CNT"]])
                            self.input_dict["ITER_CNT"] += 1
                        else:
                            throughput = throughput_estimator.get_throughput_est()
                            print("== %f ==" %throughput)
                            stime = time.time()
                            # input_dict["buffer_plan"] = mpc_sv(input_dict["events_record"], probability_weights, bitrate, throughput)
                            # input_dict["buffer_plan"] = prob_mpc(input_dict["events_record"], probability_weights, bitrate, throughput)

                            input_dict["buffer_plan"] = prob_tree_sv(input_dict["events_record"], probability_weights, bitrate, throughput)
                            etime = time.time()
                            print("Compute Time: %f" %(etime - stime))
                            self.input_dict["ITER_CNT"] += 1

                    input_dict["info_phase"] = False

                    # print(str(post_data['playerId']) + " " + str(post_data['currentPlayerIdx']))


                    idx = post_data['playerId'] - post_data['currentPlayerIdx']

                    if idx < 0:
                        idx += 5

                    return_code = input_dict["buffer_plan"][idx]

                    send_data = str.encode(str(return_code))

                    if return_code != -2:
                        lastRequestv = post_data['lastRequest']
                        currentPlayerIdxv = post_data['currentPlayerIdx']
                        playerIdv = post_data['playerId']
                        lastquality = post_data['lastquality']
                        print("""lastRequest: %d, currentPlayerIdx: %d, playerId: %d, lastquality"""%(lastRequestv, currentPlayerIdxv, playerIdv))
                        print(lastquality)
                        print(parse_vid(post_data['url']))

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.send_header('Content-Length', len(send_data))
                    self.send_header('Access-Control-Allow-Origin', "*")
                    self.end_headers()
                    self.wfile.write(send_data)


        def do_GET(self):
            print('GOT REQ')
            self.send_response(200)
            #self.send_header('Cache-Control', 'Cache-Control: no-cache, no-store, must-revalidate max-age=0')
            self.send_header('Cache-Control', 'max-age=3000')
            self.send_header('Content-Length', 20)
            self.end_headers()
            self.wfile.write("console.log('here');")

        def log_message(self, format, *args):
            return

    return Request_Handler


def run(server_class=HTTPServer, port=8333,  log_file_path=LOG_FILE):

    logger = DataLogger(log_file_path)
    throughput_estimator = ThroughputEstimator()
    logger.open()

    input_dict = {}
    input_dict["info_phase"] = True
    input_dict["ITER_CNT"] = 0
    input_dict["buffer_plan"] = [-2 for i in range(5)]
    input_dict["events_record"] = [{} for i in range(5)]

    # interface to abr server
    handler_class = make_request_handler(input_dict=input_dict, logger=logger, throughput_estimator=throughput_estimator)

    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    print ('Listening on port ' + str(port))
    httpd.serve_forever()


def main(args):
    run(log_file_path=args.logfile)

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--playtrace', default="/home/acer/Documents/reverse-tiktok/data/trace-3.0-swipe-2/trace-3.0-swipe-2-play.csv", help='Play sequence')
        parser.add_argument('--lamda', default=2)
        parser.add_argument('--logfile', default='./out.log', help='The path to save processed data')
        args = parser.parse_args()

        probability_map = get_probability_map(args.playtrace, float(args.lamda))

        main(args)
    except KeyboardInterrupt:
        print ("Keyboard interrupted.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
