import os
import xml.etree.ElementTree as ET
import re
import numpy as np
import json
import argparse
import csv
import time

# CHUNK_LENGTH = 5.0  # 5 seconds

class videoPlayer:


    def __init__(self):
        self.vsize = []
        self.segtime = []
        self.last_request_idx = -1
        self.uid = ""
        self.duration = 0
        # self.play_start_time = -1
        self.current_play_chunk_id = -1
        self.last_quality = -1
        self.last_chunk_starttime = -1
        self.last_chunk_finishtime = 0
        self.current_play_chunk_ts = 0
        self.swipetime = 0

    def update_buffering_start_time(self, last_chunk_starttime):
        self.last_chunk_starttime = last_chunk_starttime

    def update_buffering_event(
        self,
        last_quality,
        last_request_idx,
        last_chunk_finishtime,
    ):
        self.last_quality = last_quality
        self.last_request_idx = last_request_idx
        self.last_chunk_finishtime = last_chunk_finishtime

    # def update_swipe_event(self, timestamp):
    #     self.play_start_time = timestamp

    def update_chunk_play_time(self, chunk_idx, timestamp):
        self.current_play_chunk_id = chunk_idx
        self.current_play_chunk_ts = max(timestamp, self.current_play_chunk_ts)

    def _parseTime(self, path):

        tree = ET.parse(path + "/manifest.mpd")

        root = tree.getroot()

        field = root.attrib["mediaPresentationDuration"]
        num_str = re.sub("[^0-9.]", "", field)

        return float(num_str)

    def loadFromFile(self, uid, folder, bit_rates):
        self.uid = uid
        path = folder + uid

        duration = self._parseTime(path)

        self.duration = duration

        bit_rates = sorted(bit_rates)

        # print(f"{uid} {nseg}")

        first_chunk_size = 1024000

        for j in range(len(bit_rates)):
            self.vsize.append([])
            self.segtime.append([])

            total_file_size = bit_rates[j] / 8 * duration



            if total_file_size > first_chunk_size:
                self.vsize[j].append(first_chunk_size)
                self.vsize[j].append(total_file_size - first_chunk_size)

                first_chunk_time = first_chunk_size / (bit_rates[j] / 8)
                self.segtime[j].append(first_chunk_time)
                self.segtime[j].append(duration - first_chunk_time)

            else:
                self.vsize[j].append(total_file_size)
                self.segtime[j].append(duration)



IDX_DURATION = 1

IDX_SEQ = 0
IDX_URI = 1
IDX_TOTAL_DURATION = 2
IDX_BITRATE = 3
folder = "/home/acer/Documents/ttstream/contentServer/dash/data/"
class env:

    def loadSwipe(self, tracename):
        swipe_percentage = np.loadtxt(tracename)

        nlen = min(len(swipe_percentage), len(self.swipe_trace))

        for i in range(nlen):
            self.swipe_trace[i][1] = self.swipe_trace[i][0] * swipe_percentage[i]

    def loadSequence(self, seqname):
        # self.seq_map = {}
        self.swipe_trace = []
        self.sequence = []
        self.sequenceToBitrate = {}

        vp = videoPlayer()

        row_cnt = 0
        with open(seqname, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:

                duration = vp._parseTime(folder + row[IDX_URI])

                # duration = float(row[IDX_TOTAL_DURATION])

                bitrate_choices = row[IDX_BITRATE].split("&")

                if row[IDX_URI] not in self.sequenceToBitrate.keys():
                    self.sequenceToBitrate[row[IDX_URI]] = []
                    for item in bitrate_choices:
                        self.sequenceToBitrate[row[IDX_URI]].append(int(item))


                self.swipe_trace.append([duration, 0, int(row[IDX_SEQ])])
                self.sequence.append(row[IDX_URI])

                row_cnt += 1


    def getbitrate(self, throughput, bitrate_list):

        if len(throughput) == 0:
            return 0

        max_bitrate = int(bitrate_list[-1] / 1000 / 1000 * 10)

        tp = int(throughput[-1])

        bitrate_idx = len(bitrate_list) - 1

        if ((tp, max_bitrate) in self.bitrate_dict.keys()):

            target_bitrate = self.bitrate_dict[(tp, max_bitrate)] * bitrate_list[-1]

            bitrate_idx = 0

            min_diff = 1000000000000.0

            for i in range(len(bitrate_list)):
                if abs(bitrate_list[i] - target_bitrate) < min_diff:
                    bitrate_idx = i
                    min_diff = abs(bitrate_list[i] - target_bitrate)

        return bitrate_idx

    # should be linked to abr algorithm later
    def getNextBuffer(
        self, player_list, current_player_idx, current_player_idx_absolute, current_ts, bitrate_record
    ):
        # current_player_idx_absolute
        if player_list[current_player_idx].last_request_idx == -1:
            bitrate_now = self.sequenceToBitrate[self.sequence[current_player_idx_absolute]]
            bitrate_now = sorted(bitrate_now)
            idx = self.getbitrate(self.throughput_history, bitrate_now)

            bitrate_record[current_player_idx_absolute] = bitrate_now[idx]

            return (current_player_idx, player_list[current_player_idx].last_request_idx + 1, idx)

        if player_list[current_player_idx].last_request_idx + 1 < len(player_list[current_player_idx].vsize[player_list[current_player_idx].last_quality]):
            return (current_player_idx, player_list[current_player_idx].last_request_idx + 1, player_list[current_player_idx].last_quality)

        for i in range(1, 5):
            real_i = (current_player_idx + i) % 5

            if player_list[real_i].last_request_idx == -1:
                bitrate_now = self.sequenceToBitrate[self.sequence[current_player_idx_absolute + i]]
                bitrate_now = sorted(bitrate_now)

                idx = self.getbitrate(self.throughput_history, bitrate_now)

                if current_player_idx_absolute + i < len(bitrate_record):
                    bitrate_record[current_player_idx_absolute + i] = bitrate_now[idx]

                return (real_i, player_list[real_i].last_request_idx + 1, idx)
        return (-1, -1, -1)


    def timeToDownload(self, filesize, real_time):

        while real_time >= len(self.time_to_packetidx):
            real_time -= len(self.time_to_packetidx)

        self.time_idx = self.time_to_packetidx[int(real_time)]

        while self.time_idx >= len(self.networktrace):
            self.time_idx -= len(self.networktrace)

        n_packets = int(filesize/1500.0 / 0.8)

        if self.time_idx + n_packets >= len(self.networktrace):
            time_in_ms = self.networktrace[self.time_idx + n_packets - len(self.networktrace)] + self.networktrace[len(self.networktrace) - 1] - self.networktrace[self.time_idx]
        else:
            time_in_ms = self.networktrace[self.time_idx + n_packets] - self.networktrace[self.time_idx]

        time_in_ms = max(time_in_ms, 1)

        print(time_in_ms / 1000.0)

        return time_in_ms / 1000.0

    def init_throughput(self, trace):
        throughput_discount = 0.8
        self.network_throughput = [0] * (int(trace[-1] / 1000) + 1)

        for i in range(len(trace)):
            idx = int(trace[i] / 1000)

            self.network_throughput[idx] += 1

        for i in range(len(self.network_throughput)):
            self.network_throughput[i] = self.network_throughput[i] * 1500 * 8 / 1000 * throughput_discount

    def __init__(self, seqname, traceanme, networktracename):

        self.loadSequence(seqname)

        self.loadSwipe(traceanme)

        self.buffer_map = {}
        self.instance_map = {}

        self.player_num = 5

        self.buffer_list = [0 for i in range(self.player_num)]

        self.video_name = ["" for i in range(self.player_num)]

        self.current_player_idx = 0

        self.player_bit = 0

        self.networktracename = networktracename
        self.networktrace = np.loadtxt(networktracename)

        self.time_to_packetidx = [0] * (int(self.networktrace[-1] / 1000) + 2)

        for pk_time in self.networktrace:
            self.time_to_packetidx[int(pk_time / 1000) + 1] += 1

        for i in range(1, len(self.time_to_packetidx)):
            self.time_to_packetidx[i] += self.time_to_packetidx[i-1]


        self.init_throughput(self.networktrace)
        self.time_idx = 0
        self.throughput_history = []

        self.bitrate_dict = {}

        bitrate_data = np.loadtxt("../abr_server/bitrate_table.log")

        for i in range(len(bitrate_data)):
            self.bitrate_dict[(int(bitrate_data[i][0]), int(bitrate_data[i][1]))] = bitrate_data[i][2]

        # tmp = 1


    def estimate_throughput(self, current_ts):
        net_trace_time = self.networktrace[-1] / 1000

        while current_ts > net_trace_time:
            current_ts -= net_trace_time

        look_ahead_time = 10

        ts_idx = int(current_ts)

        t_len = len(self.network_throughput)

        total_tp = 0

        for i in range(look_ahead_time):

            total_tp += self.network_throughput[(ts_idx + i) % t_len]

        mean_tp = total_tp / look_ahead_time

        return mean_tp

    def load_new_video(self, view_vidx, player_list):

        player_list[self.current_player_idx] = videoPlayer()
        player_list[self.current_player_idx].loadFromFile(
            self.sequence[view_vidx + self.player_num], folder,
            self.sequenceToBitrate[self.sequence[view_vidx + self.player_num]]
        )
        player_list[self.current_player_idx].swipetime = self.swipe_trace[view_vidx + self.player_num][IDX_DURATION]


    def run(self):
        real_time = 0

        view_vidx = 0
        view_cidx = 0

        threshould = 80

        download_time_dict = {}


        player_list = []
        for i in range(self.player_num):
            player_list.append(videoPlayer())

            player_list[i].loadFromFile(self.sequence[i], folder, self.sequenceToBitrate[self.sequence[i]])
            player_list[i].swipetime = self.swipe_trace[i][IDX_DURATION]

        last_buffer_player_idx = -1

        unfinished_record_play = []
        unfinished_record_download = []

        # player_list[0].update_swipe_event(0.0)
        player_list[0].update_chunk_play_time(0, 0.0)

        # todo: current_view_end_time can be changed
        current_view_end_time = self.swipe_trace[0][IDX_DURATION]

        video_rebuffer_record = [0] * (threshould + 1)
        video_bitrate_record = [0] * (threshould + 1)

        while view_vidx <= threshould:
            # need to change
            view_duration = self.swipe_trace[view_vidx][IDX_DURATION]
            self.current_player_idx = view_vidx % self.player_num

            # rebuffering starts
            if (view_vidx, view_cidx) not in download_time_dict.keys():

                print(f"in rebuffering {view_vidx} {view_cidx}")

                if len(unfinished_record_download) == 0:
                    result = self.getNextBuffer(
                        player_list,
                        self.current_player_idx,
                        view_vidx,
                        real_time,
                        video_bitrate_record,
                    )

                    player_id = result[0]
                    chunk_id = result[1]
                    quality = result[2]

                    if player_id != -1:

                        player_list[player_id].update_buffering_start_time(real_time)

                        filesize = (
                            player_list[player_id].vsize[quality][chunk_id]
                        )

                        time_to_download_finish = self.timeToDownload(filesize, real_time)

                        # self.start_download(filesize)

                        self.throughput_history.append(filesize * 8 / 1000 / 1000 / time_to_download_finish)

                    else:
                        time_to_download_finish = -1

                else:
                    result = unfinished_record_download[1]

                    player_id = result[0]
                    chunk_id = result[1]
                    quality = result[2]

                    time_to_download_finish = unfinished_record_download[0]

                if time_to_download_finish == -1:
                    print(f"====== error =============")

                player_list[player_id].update_buffering_event(
                    quality, chunk_id, real_time + time_to_download_finish
                )

                if (real_time + time_to_download_finish < current_view_end_time):
                    video_rebuffer_record[view_vidx] += time_to_download_finish
                    real_time += time_to_download_finish

                else:
                    video_rebuffer_record[view_vidx] += (current_view_end_time - real_time)
                    real_time = current_view_end_time

                    if view_vidx + self.player_num >= len(self.sequence):
                        break

                    self.load_new_video(view_vidx, player_list)
                    if player_id == self.current_player_idx:
                        unfinished_record_download = []
                        # chunk downloading is abandoned due to the swipe

                    view_vidx += 1
                    view_cidx = 0

                    current_view_end_time += self.swipe_trace[view_vidx][IDX_DURATION]

                    unfinished_record_play = []

                    continue


                # if the played chunk is in the rebuffering state, update the real start playing chunk time with the time when the download finishes
                # if chunk_id == player_list[player_id].current_play_chunk_id:
                player_list[self.current_player_idx].update_chunk_play_time(view_cidx, real_time)

                real_player_id = -3

                for id in range(self.player_num):
                    if (view_vidx + id) % self.player_num == player_id:
                        real_player_id = view_vidx + id

                if real_player_id == -3:
                    tmp = 1

                download_time_dict[(real_player_id, chunk_id)] = real_time
                print("d %d %d %f %d" % (real_player_id, chunk_id, real_time, quality))

                unfinished_record_download = []

            else:

                print("in normal play")
                # should consider the remaining time from the last event
                if len(unfinished_record_download) == 0:
                    result = self.getNextBuffer(
                        player_list,
                        self.current_player_idx,
                        view_vidx,
                        real_time,
                        video_bitrate_record,
                    )

                    player_id = result[0]
                    chunk_id = result[1]
                    quality = result[2]

                    if player_id != -1:

                        player_list[player_id].update_buffering_start_time(real_time)

                        filesize = (
                            player_list[player_id].vsize[quality][chunk_id]
                        )

                        time_to_download_finish = self.timeToDownload(filesize, real_time)

                        # self.start_download(filesize)

                        # try:
                        self.throughput_history.append(filesize * 8 / 1000 / 1000 / time_to_download_finish)
                        # except:
                        #     tmp = 1

                    else:
                        time_to_download_finish = -1

                else:
                    result = unfinished_record_download[1]

                    player_id = result[0]
                    chunk_id = result[1]
                    quality = result[2]

                    time_to_download_finish = unfinished_record_download[0]

                if len(unfinished_record_play) == 0:
                    time_to_view_finish = player_list[view_vidx % 5].segtime[player_list[view_vidx % 5].last_quality][view_cidx]
                else:
                    time_to_view_finish = unfinished_record_play[0]

                if (
                    time_to_download_finish != -1
                    and time_to_download_finish < time_to_view_finish
                ):

                    player_list[player_id].update_buffering_event(
                        quality,
                        chunk_id,
                        real_time + time_to_download_finish,
                    )

                    if (real_time + time_to_download_finish < current_view_end_time):
                        real_time += time_to_download_finish
                    else:
                        unfinished_record_download = [
                            real_time + time_to_download_finish - current_view_end_time,
                            (player_id, chunk_id, quality),
                        ]

                        real_time = current_view_end_time

                        if view_vidx + self.player_num >= len(self.sequence):
                            break
                        self.load_new_video(view_vidx, player_list)



                        if player_id == self.current_player_idx:
                            unfinished_record_download = []
                            # chunk downloading is abandoned due to the swipe

                        view_vidx += 1
                        view_cidx = 0

                        current_view_end_time += self.swipe_trace[view_vidx][IDX_DURATION]

                        unfinished_record_play = []

                        continue

                    # real_time += time_to_download_finish

                    real_player_id = -2

                    for id in range(self.player_num):
                        if (view_vidx + id) % self.player_num == player_id:
                            real_player_id = view_vidx + id

                    download_time_dict[(real_player_id, chunk_id)] = real_time
                    # print(real_player_id, chunk_id)

                    print("d %d %d %f %d" % (real_player_id, chunk_id, real_time, quality))

                    unfinished_record_play = [
                        time_to_view_finish - time_to_download_finish
                    ]
                    unfinished_record_download = []

                else:

                    unfinished_record_download = [
                        time_to_download_finish - time_to_view_finish,
                        (player_id, chunk_id, quality),
                    ]
                    unfinished_record_play = []

                    if time_to_download_finish == -1:
                        unfinished_record_download = []

                    # real_time += time_to_view_finish

                    if (real_time + time_to_view_finish < current_view_end_time - 0.0001):
                        real_time += time_to_view_finish

                        # play next chunk
                        view_cidx += 1

                        player_list[self.current_player_idx].update_chunk_play_time(
                            view_cidx, real_time
                        )

                        print("p %d %d %f" % (self.current_player_idx, view_cidx, real_time))

                    else:
                        real_time = current_view_end_time

                        if view_vidx + self.player_num >= len(self.sequence):
                            break
                        self.load_new_video(view_vidx, player_list)
                        if player_id == self.current_player_idx:
                            unfinished_record_download = []
                            # chunk downloading is abandoned due to the swipe

                        view_vidx += 1
                        view_cidx = 0

                        current_view_end_time += self.swipe_trace[view_vidx][IDX_DURATION]

                        unfinished_record_play = []

        print(self.throughput_history)
        # self.exit_server()

        fd = open(args.logfile, "w")
        for i in range(min(threshould + 1, len(self.swipe_trace))):
            rebuffering = video_rebuffer_record[i]
            reward = video_bitrate_record[i] / 8 * (self.swipe_trace[i][IDX_DURATION] - rebuffering)

            str = f"{rebuffering} {int(reward / 1000)} {i} {self.swipe_trace[i][IDX_DURATION]}\n"

            # print(str)
            fd.write(str)
        fd.close()

        # fd.write(f"{rebuffering} {int(reward / 1000)} {i} {swipe_log[i + 1] - swipe_log[i]}\n")

def main(args):
    # seqname = "/home/acer/Documents/ttstream/testing/dataclean/vid.json"
    e = env(args.playtrace, args.swipetrace, args.networktrace)
    e.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--playtrace', default="/home/acer/Documents/reverse-tiktok/data/trace-19.5-swipe-3/trace-19.5-swipe-3-play.csv", help='Play sequence')
    parser.add_argument('--swipetrace', default="/home/acer/Documents/reverse-tiktok/traces/swipe/swipe-3.txt", help='Viewing trace')
    parser.add_argument('--networktrace', default="/home/acer/Documents/reverse-tiktok/traces/network/trace-19.5.down", help='The network trace')
    parser.add_argument('--logfile', default="./tt.log", help='The log path')
    # parser.add_argument('--probabilitytraces', default='./data', help='The path to save processed data')
    # time.sleep(3)
    args = parser.parse_args()
    main(args)
