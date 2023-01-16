import os
import xml.etree.ElementTree as ET
import re
import numpy as np
import json
import requests
import argparse
import csv
import time

CHUNK_LENGTH = 5.0  # 5 seconds

class videoPlayer:


    def __init__(self):
        self.nchunks = 0
        self.vsize = []
        self.segtime = []
        self.last_request_idx = -1
        self.uid = ""
        self.duration = 0
        self.play_start_time = -1
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

    def update_swipe_event(self, timestamp):
        self.play_start_time = timestamp

    def update_chunk_play_time(self, chunk_idx, timestamp):
        self.current_play_chunk_id = chunk_idx
        self.current_play_chunk_ts = max(timestamp, self.current_play_chunk_ts)

    def _parseTime(self, path):

        if "realtime" in path:
            return 0.1

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

        nseg = int(duration / CHUNK_LENGTH)

        if duration - nseg * CHUNK_LENGTH > 0.00000001:
            nseg += 1

        self.nchunks = nseg

        bit_rates = sorted(bit_rates)

        # print(f"{uid} {nseg}")

        for i in range(int(duration - 0.00000001) + 1):
            idx = int(i / CHUNK_LENGTH)
            if i % int(CHUNK_LENGTH) == 0:
                seg_time = min(duration - idx * CHUNK_LENGTH, CHUNK_LENGTH)
                self.segtime.append(seg_time)

                self.vsize.append([])

                for j in range(len(bit_rates)):
                    self.vsize[idx].append(bit_rates[j] * seg_time / 8)


IDX_DURATION = 1

IDX_SEQ = 0
IDX_URI = 1
IDX_TOTAL_DURATION = 2
IDX_BITRATE = 3
folder = "/home/acer/Documents/ttstream/contentServer/dash/data/"

row_addition = ['realtime', '100', '200000']
class env:

    def loadSwipe(self, tracename):
        swipe_percentage = np.loadtxt(tracename)

        nlen = min(len(swipe_percentage), len(self.swipe_trace))

        for i in range(nlen - 1):
            self.swipe_trace[i][1] = swipe_percentage[i+1] - swipe_percentage[i]
            self.swipe_trace[i][1] = min(self.swipe_trace[i][1], self.swipe_trace[i][0])

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
                if len(row) == 1:
                    row.extend(row_addition)
                #     duration = 0.1
                # else:
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

    # should be linked to abr algorithm later
    def getNextBuffer(
        self, player_list, current_player_idx, current_player_idx_absolute, current_ts
    ):

        oracle_throughput = self.estimate_throughput(current_ts)

        print(f"current ts: {current_ts}")

        for i in range(len(player_list)):

            ret = self.sendAbrRequest(player_list[i], i, current_player_idx, current_ts, 1, oracle_throughput, current_player_idx_absolute)

        buffer_player = -1
        buffer_quality = -1
        for i in range(len(player_list)):

            ret = self.sendAbrRequest(player_list[i], i, current_player_idx, current_ts, 0, oracle_throughput, current_player_idx_absolute)
            if ret != -2:
                buffer_player = i
                buffer_quality = ret

        if buffer_player == -1:
            return (-1, -1, -1)

        return (
            buffer_player,
            player_list[buffer_player].last_request_idx + 1,
            buffer_quality,
        )


    # should be linked to abr algorithm later
    def exit_server(self):
        pload = {
            "isinfo": -1,
        }

        data_json = json.dumps(pload)

        r = requests.post("http://localhost:8333", data=data_json)




    def timeToDownload(self, filesize, real_time):

        while real_time >= len(self.time_to_packetidx):
            real_time -= len(self.time_to_packetidx)

        self.time_idx = self.time_to_packetidx[int(real_time)]

        while self.time_idx >= len(self.networktrace):
            self.time_idx -= len(self.networktrace)

        n_packets = int(filesize/1500.0 / 0.5)

        if self.time_idx + n_packets >= len(self.networktrace):
            time_in_ms = self.networktrace[self.time_idx + n_packets - len(self.networktrace)] + self.networktrace[len(self.networktrace) - 1] - self.networktrace[self.time_idx]
        else:
            time_in_ms = self.networktrace[self.time_idx + n_packets] - self.networktrace[self.time_idx]
        
        print(time_in_ms / 1000.0)

        return time_in_ms / 1000.0


    def init_throughput(self, trace):
        throughput_discount = 0.5
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

    def sendAbrRequest(self, player, playerId, current_player_idx, current_ts, isinfo, oracle_throughput, current_player_idx_abusolute):
        next_chunk_size = []

        cid = player.last_request_idx + 1

        if cid == len(player.vsize):
            for i in range(len(player.vsize[0])):
                next_chunk_size.append(0)

        else:
            for i in range(len(player.vsize[cid])):
                next_chunk_size.append(player.vsize[cid][i])

        last_chunk_size = 0
        bandwidth_est = 0

        if player.last_request_idx >= 0:
            last_chunk_size = player.vsize[player.last_request_idx][player.last_quality]

            # if player.last_chunk_finishtime - player.last_chunk_starttime == 0:
            #     tmp = 1

            bandwidth_est = (
                last_chunk_size
                * 8
                / (player.last_chunk_finishtime - player.last_chunk_starttime)
                / 1000
            )

        # get the rebuffer time
        rebuffer_time = 0
        if player.play_start_time != -1:
            rebuffer_time = current_ts - player.play_start_time

            if player.current_play_chunk_id != -1:
                rebuffer_time -= player.current_play_chunk_id * CHUNK_LENGTH + (current_ts - player.current_play_chunk_ts)

                print(f"chunk progress: {current_ts - player.current_play_chunk_ts}")

                if current_ts - player.current_play_chunk_ts > CHUNK_LENGTH:
                    tmp = 1
        # print(f"rebuffer time: {rebuffer_time}")

        # get the buffer length
        buffer_length = 0
        if player.last_request_idx != -1:
            for i in range(player.last_request_idx + 1):
                buffer_length += player.segtime[i]

            if player.current_play_chunk_id != -1:
                buffer_length -= player.current_play_chunk_id * CHUNK_LENGTH + (current_ts - player.current_play_chunk_ts)

        if buffer_length < 0:
            tmp = 1
        # print(f"buffer: {buffer_length}")

        realPlayerId = (playerId - current_player_idx + 5) % 5 + current_player_idx_abusolute

        pload = {
            "nextChunkSize": next_chunk_size,
            "Type": "download",
            "lastquality": player.last_quality,
            "buffer": buffer_length,
            "bandwidthEst": bandwidth_est,
            "lastRequest": player.last_request_idx,
            "RebufferTime": rebuffer_time,
            "lastChunkFinishTime": player.last_chunk_finishtime * 1000,
            "lastChunkStartTime": player.last_chunk_starttime * 1000,
            "lastChunkSize": last_chunk_size,
            "playerId": playerId,
            "realPlayerId": realPlayerId,
            "currentPlayerIdx": current_player_idx,
            "url": "http://172.29.130.16:8080/dash/data/%s/manifest.mpd" % player.uid,
            "duration": player.duration,
            "isinfo": isinfo,
            "currentTime": current_ts,
            "chunksize_list": player.vsize,
            "oracle_swipetime": player.swipetime,
            "oracle_throughput": oracle_throughput,
        }

        # print(player.vsize)

        data_json = json.dumps(pload)

        r = requests.post("http://localhost:8333", data=data_json)

        return int(r.text)

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

        player_list[0].update_swipe_event(0.0)
        player_list[0].update_chunk_play_time(0, 0.0)

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
                    )

                    player_id = result[0]
                    chunk_id = result[1]
                    quality = result[2]

                    if player_id != -1:

                        player_list[player_id].update_buffering_start_time(real_time)

                        filesize = (
                            player_list[player_id].vsize[chunk_id][quality]
                        )

                        time_to_download_finish = self.timeToDownload(filesize, real_time)

                    else:
                        time_to_download_finish = -1

                else:
                    result = unfinished_record_download[1]

                    player_id = result[0]
                    chunk_id = result[1]
                    quality = result[2]

                    time_to_download_finish = unfinished_record_download[0]

                player_list[player_id].update_buffering_event(
                    quality, chunk_id, real_time + time_to_download_finish
                )

                real_time += time_to_download_finish

                # if the played chunk is in the rebuffering state, update the real start playing chunk time with the time when the download finishes
                # if chunk_id == player_list[player_id].current_play_chunk_id:
                player_list[self.current_player_idx].update_chunk_play_time(view_cidx, real_time)

                real_player_id = -3

                for id in range(self.player_num):
                    if (view_vidx + id) % self.player_num == player_id:
                        real_player_id = view_vidx + id

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
                    )

                    player_id = result[0]
                    chunk_id = result[1]
                    quality = result[2]

                    if player_id != -1:

                        player_list[player_id].update_buffering_start_time(real_time)

                        filesize = (
                            player_list[player_id].vsize[chunk_id][quality]
                        )

                        time_to_download_finish = self.timeToDownload(filesize, real_time)

                    else:
                        time_to_download_finish = -1

                else:
                    result = unfinished_record_download[1]

                    player_id = result[0]
                    chunk_id = result[1]
                    quality = result[2]

                    time_to_download_finish = unfinished_record_download[0]

                if len(unfinished_record_play) == 0:
                    time_to_view_finish = min(
                        view_duration - (view_cidx * CHUNK_LENGTH),
                        CHUNK_LENGTH,
                    )
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

                    real_time += time_to_download_finish

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

                    real_time += time_to_view_finish

                    if (
                        view_duration - (view_cidx * CHUNK_LENGTH) - 0.00000001
                        < CHUNK_LENGTH
                    ):
                        # swipe happens

                        if view_vidx + self.player_num >= len(self.sequence):
                            break

                        print(player_list[self.current_player_idx].uid)
                        player_list[self.current_player_idx] = videoPlayer()
                        player_list[self.current_player_idx].loadFromFile(
                            self.sequence[view_vidx + self.player_num], folder, self.sequenceToBitrate[self.sequence[view_vidx + self.player_num]]
                        )
                        player_list[self.current_player_idx].swipetime = self.swipe_trace[view_vidx + self.player_num][IDX_DURATION]

                        print(player_list[self.current_player_idx].uid)
                        if player_id == self.current_player_idx:
                            unfinished_record_download = []
                            # chunk downloading is abandoned due to the swipe

                        view_vidx += 1
                        view_cidx = 0

                        player_list[view_vidx % self.player_num].update_swipe_event(
                            real_time
                        )

                    else:
                        # play next chunk
                        view_cidx += 1

                        player_list[self.current_player_idx].update_chunk_play_time(
                            view_cidx, real_time
                        )

                        print("p %d %d %f" % (self.current_player_idx, view_cidx, real_time))

        self.exit_server()

def main(args):
    # seqname = "/home/acer/Documents/ttstream/testing/dataclean/vid.json"
    e = env(args.playtrace, args.swipetrace, args.networktrace)
    e.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--playtrace', default="/home/acer/Documents/reverse-tiktok/data/tt-102-high/tt-102-high-play.csv", help='Play sequence')
    parser.add_argument('--swipetrace', default="/home/acer/Documents/reverse-tiktok/data/tt-102-high/tt-102-high-swipe-time.logxyz", help='Viewing trace')
    parser.add_argument('--networktrace', default="/home/acer/Documents/reverse-tiktok/traces/user-study/trace-high.down", help='The network trace')
    # parser.add_argument('--probabilitytraces', default='./data', help='The path to save processed data')
    time.sleep(3)
    args = parser.parse_args()
    main(args)
