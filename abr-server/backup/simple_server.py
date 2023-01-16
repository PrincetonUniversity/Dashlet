#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import base64
import urllib
import sys
import os
import json
import time
os.environ['CUDA_VISIBLE_DEVICES']=''

import numpy as np
import time
import itertools

################## ROBUST MPC ###################

S_INFO = 5  # bit_rate, buffer_size, rebuffering_time, bandwidth_measurement, chunk_til_video_end
S_LEN = 8  # take how many frames in the past
MPC_FUTURE_CHUNK_COUNT = 5
VIDEO_BIT_RATE = [300,750,1200,1850,2850,4300]  # Kbps
BITRATE_REWARD = [1, 2, 3, 12, 15, 20]
BITRATE_REWARD_MAP = {0: 0, 300: 1, 750: 2, 1200: 3, 1850: 12, 2850: 15, 4300: 20}
M_IN_K = 1000.0
BUFFER_NORM_FACTOR = 10.0
CHUNK_TIL_VIDEO_END_CAP = 48.0
TOTAL_VIDEO_CHUNKS = 48
DEFAULT_QUALITY = 0  # default video quality without agent
REBUF_PENALTY = 4.3  # 1 sec rebuffering -> this number of Mbps
SMOOTH_PENALTY = 1
TRAIN_SEQ_LEN = 100  # take as a train batch
MODEL_SAVE_INTERVAL = 100
RANDOM_SEED = 42
RAND_RANGE = 1000
SUMMARY_DIR = './results'
LOG_FILE = './results/log'
# in format of time_stamp bit_rate buffer_size rebuffer_time video_chunk_size download_time reward
NN_MODEL = None

CHUNK_COMBO_OPTIONS = []

# past errors in bandwidth
past_errors = []
past_bandwidth_ests = []


def get_chunk_size(quality, index):
    return 1000

def parse_vid(url):
    return url.split("/")[5]


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

def make_request_handler(input_dict, logger):

    class Request_Handler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.input_dict = input_dict
            self.log_file = input_dict['log_file']
            #self.saver = input_dict['saver']
            self.s_batch = input_dict['s_batch']
            #self.a_batch = input_dict['a_batch']
            #self.r_batch = input_dict['r_batch']
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))

            # print(post_data)
            if post_data['Type'] == 'swipe':
                logger.append_swipe(post_data)

                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', 0)
                self.send_header('Access-Control-Allow-Origin', "*")
                self.end_headers()
            
            else:

                logger.append_download(post_data)

                return_code = -2

                if (post_data['playerId'] == post_data['currentPlayerIdx']):
                    return_code = len(post_data['nextChunkSize'])-1
                    

                    # if (post_data['playerId'] == (post_data['currentPlayerIdx']+1)%8):
                    #     if (post_data['lastRequest'] < 3):
                    #         return_code = len(post_data['nextChunkSize'])-1
                    
                    # if (post_data['lastRequest'] < 0):
                    #     return_code = len(post_data['nextChunkSize'])-1

                
                send_data = str(return_code)
                
                # print """lastRequest: %d, currentPlayerIdx: %d, playerId: %d"""%(lastRequestv, currentPlayerIdxv, playerIdv)

                if return_code != -2:
                    lastRequestv = post_data['lastRequest']
                    currentPlayerIdxv = post_data['currentPlayerIdx']
                    playerIdv = post_data['playerId']
                    lastquality = post_data['lastquality']
                    print """lastRequest: %d, currentPlayerIdx: %d, playerId: %d, lastquality"""%(lastRequestv, currentPlayerIdxv, playerIdv)
                    print lastquality
                    print parse_vid(post_data['url'])
                    print "return " + send_data
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', len(send_data))
                self.send_header('Access-Control-Allow-Origin', "*")
                self.end_headers()
                self.wfile.write(send_data)

                # record [state, action, reward]
                # put it here after training, notice there is a shift in reward storage

                # if end_of_video:
                #     self.s_batch = [np.zeros((S_INFO, S_LEN))]
                # else:
                #     self.s_batch.append(state)

        def do_GET(self):
            print >> sys.stderr, 'GOT REQ'
            self.send_response(200)
            #self.send_header('Cache-Control', 'Cache-Control: no-cache, no-store, must-revalidate max-age=0')
            self.send_header('Cache-Control', 'max-age=3000')
            self.send_header('Content-Length', 20)
            self.end_headers()
            self.wfile.write("console.log('here');")

        def log_message(self, format, *args):
            return

    return Request_Handler


def run(server_class=HTTPServer, port=8333, log_file_path=LOG_FILE):

    logger = DataLogger("empc-short.log")
    logger.open()
    np.random.seed(RANDOM_SEED)

    if not os.path.exists(SUMMARY_DIR):
        os.makedirs(SUMMARY_DIR)

    # make chunk combination options
    for combo in itertools.product([0,1,2,3,4,5], repeat=5):
        CHUNK_COMBO_OPTIONS.append(combo)

    with open(log_file_path, 'wb') as log_file:

        s_batch = [np.zeros((S_INFO, S_LEN))]

        last_bit_rate = DEFAULT_QUALITY
        last_total_rebuf = 0
        # need this storage, because observation only contains total rebuffering time
        # we compute the difference to get

        video_chunk_count = 0

        input_dict = {'log_file': log_file,
                      'last_bit_rate': last_bit_rate,
                      'last_total_rebuf': last_total_rebuf,
                      'video_chunk_coount': video_chunk_count,
                      's_batch': s_batch}

        # interface to abr_rl server
        handler_class = make_request_handler(input_dict=input_dict, logger=logger)

        server_address = ('localhost', port)
        httpd = server_class(server_address, handler_class)
        print 'Listening on port ' + str(port)
        httpd.serve_forever()


def main():
    if len(sys.argv) == 2:
        trace_file = sys.argv[1]
        run(log_file_path=LOG_FILE + '_robustMPC_' + trace_file)
    else:
        run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Keyboard interrupted."
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
