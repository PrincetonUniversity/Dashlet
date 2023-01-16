#!/usr/bin/env python

import base64
import copy
import urllib
import sys
import os
import json
from util import bufferTraceGenerator
from util import swipeTraceGenerator


import numpy as np
import time
import itertools
from itertools import permutations


stime = time.time()


bitraterewards = [1143, 2064, 4449, 6086, 9193, 0]
chunklength = 5.00

penalty_weight = 9193

CHUNK_COMBO_OPTIONS_ALL = []
CHUNK_COMBO_OPTIONS_ALL.append([])
for i in range(1, 5 + 1):
    CHUNK_COMBO_OPTIONS_ALL.append([])

    for combo in itertools.product([0, 1, 2, 3, 4], repeat=i):
        CHUNK_COMBO_OPTIONS_ALL[i].append(combo)
    CHUNK_COMBO_OPTIONS_ALL[i].reverse()


"""
Parse the parameter related to buffer status
Return:
buffer_length: total buffer length in chunks (from the start)
video_duration: video duration in seconds
current_cursor: current cursor position in seconds
"""


def parse_buffer_status(events):

    buffer_length = []
    video_duration = []

    for i in range(len(events)):
        event = events[i]

        idx = event["lastRequest"] + 1

        buffer_length.append(idx)

        video_duration.append(event["duration"])

    # total buffered video in seconds - not played video in the buffer
    current_cursor = min(buffer_length[0] * 5, video_duration[0]) - events[0]["buffer"]

    return buffer_length, video_duration, current_cursor


def computeReward_entry(
    bufferseqence,
    bitratesequence,
    play_sequence,
    bitrate,
    throughput_estimator,
    buffer_length,
    video_length,
    current_cursor,
):

    # playlist
    buffertable = [
        [[-1, 0] for j in range(video_length[i])] for i in range(len(video_length))
    ]

    for i in range(len(buffer_length)):
        for j in range(buffer_length[i]):
            buffertable[i][j] = [0, -1]  # [timestamp, bitrate]

    buffertableidx = copy.deepcopy(buffer_length)

    # bufferseqence = []
    #
    # for i in range(len(bufferseqence_x)):
    #     for j in range(bufferseqence_x[i]):
    #         bufferseqence.append(i)

    timestamp = 0
    fsize_list = []
    for i in range(len(bufferseqence)):
        fsize_list.append(bitrate[bufferseqence[i]][buffertableidx[bufferseqence[i]]][bitratesequence[i]])

    ts_list = throughput_estimator.timeToDownload(fsize_list)

    for i in range(len(bufferseqence)):

        # try:
        timestamp += ts_list[i]
        # except:
        #     tmp = 1

        buffertable[bufferseqence[i]][buffertableidx[bufferseqence[i]]] = [
            timestamp,
            bitratesequence[i],
        ]

        buffertableidx[bufferseqence[i]] += 1

    # for i in range(len(playlist)):
    playsequence = []

    timestamp = 0

    totalchunk = 0
    for j in range(5):
        for k in range(play_sequence[j]):

            cur_chunk = int(current_cursor / 5.0)
            totalchunk += 1
            if j == 0:
                playsequence.append([j, k + cur_chunk, timestamp])
            else:
                playsequence.append([j, k, timestamp])

            timestamp += 5.0

    rebufferingpenalty = 0
    abrreward = 0

    has_penality = [0 for i in range(5)]


    for j in range(totalchunk):
        abrreward += bitraterewards[
            buffertable[playsequence[j][0]][playsequence[j][1]][1]
        ]

        if buffertable[playsequence[j][0]][playsequence[j][1]][0] == -1:
            if has_penality[playsequence[j][0]] == 0:

                # give high penalty here
                rebufferingpenalty += 10
                has_penality[playsequence[j][0]] = 1

        else:
            if (
                buffertable[playsequence[j][0]][playsequence[j][1]][0]
                > playsequence[j][2]
            ):
                thispenalty = max(buffertable[playsequence[j][0]][playsequence[j][1]][0] - playsequence[j][2] - rebufferingpenalty, 0)
                rebufferingpenalty += thispenalty
    reward = abrreward - penalty_weight * rebufferingpenalty

    return reward


def prob_tree_sv(events, probability_weights, bitrate_profile, throughput_estimator):
    stime = time.time()

    buffer_length, video_duration, current_cursor = parse_buffer_status(events)

    total_lengths = [int((vduration - 0.00000001) / 5.0) + 1 for vduration in video_duration]

    cursor_idx = int(current_cursor / 5.0) + 1

    nchunk = 5
    nvideos = 5

    sg = swipeTraceGenerator(
        cursor_idx, total_lengths, nchunk, nvideos, probability_weights
    )
    trace, prob_ret = sg.enumerate_traces()

    playlist = copy.deepcopy(trace)

    for i in range(len(playlist)):
        playlist[i].append(prob_ret[i])

    buffer_range_high = 1

    for i in range(nchunk):
        if buffer_length[i] > 0:
            buffer_range_high = min(5, i + 1 + 1)

    total_reward = -100000000

    max_buffer_idx = -2
    max_bitrate_idx = -2

    for buffer_idx in range(buffer_range_high):
        # in case some of the buffer is already full
        if buffer_length[buffer_idx] == total_lengths[buffer_idx]:
            continue

        need_buffer_flag = False

        for trace_idx in range(len(playlist)):

            if buffer_idx == 0:

                if playlist[trace_idx][buffer_idx] + (cursor_idx - 1) > buffer_length[buffer_idx]:
                    need_buffer_flag = True

            else:

                if playlist[trace_idx][buffer_idx] > buffer_length[buffer_idx]:
                    need_buffer_flag = True

        if need_buffer_flag == False:
            continue

        for bitrate_idx in [0, 1, 2, 3, 4]:

            reward_list = [0 for trace_idx in range(len(playlist))]

            for trace_idx in range(len(playlist)):

                bufferseqence = copy.deepcopy(playlist[trace_idx])

                combo_reward = -100000000

                total_chunk = 0
                if bufferseqence[buffer_idx] > 0:
                    bufferseqence[buffer_idx] -= 1

                bs_info = [buffer_idx]

                for bidx in range(len(buffer_length)):
                    if bidx == 0:
                         bufferseqence[bidx] -= buffer_length[bidx] - (cursor_idx - 1)
                    else:
                         bufferseqence[bidx] -= buffer_length[bidx]

                    if bufferseqence[bidx] < 0:
                        bufferseqence[bidx] = 0

                    total_chunk += bufferseqence[bidx]

                    for ti in range(bufferseqence[bidx]):
                        bs_info.append(bidx)


                CHUNK_COMBO_OPTIONS = CHUNK_COMBO_OPTIONS_ALL[total_chunk]

                for full_combo in CHUNK_COMBO_OPTIONS:
                    combo_info = [bitrate_idx]
                    combo_info.extend(full_combo)

                    reward = computeReward_entry(
                        bs_info,
                        combo_info,
                        playlist[trace_idx],
                        bitrate_profile,
                        throughput_estimator,
                        buffer_length,
                        total_lengths,
                        current_cursor,
                    )
                    combo_reward = max(combo_reward, reward)

                # if no enumeration needed
                if total_chunk == 0:
                    combo_reward = computeReward_entry(
                        bs_info,
                        [bitrate_idx],
                        playlist[trace_idx],
                        bitrate_profile,
                        throughput_estimator,
                        buffer_length,
                        total_lengths,
                        current_cursor,
                    )

                reward_list[trace_idx] = combo_reward

                # playlist[trace_idx]

            option_reward = 0
            for trace_idx in range(len(playlist)):
                option_reward += reward_list[trace_idx] * playlist[trace_idx][-1]

            # print(buffer_idx, bitrate_idx, option_reward)

            if option_reward > total_reward:
                total_reward = option_reward
                max_buffer_idx = buffer_idx
                max_bitrate_idx = bitrate_idx

    ret = [-2, -2, -2, -2, -2]
    ret[max_buffer_idx] = max_bitrate_idx
    if max_bitrate_idx >= 0:
        bitrate_todownload = bitrate_profile[max_buffer_idx][buffer_length[max_buffer_idx]][max_bitrate_idx]
        throughput_estimator.start_download(bitrate_todownload)
    print(ret)
    return ret


def prob_mpc(events, probability_weights, bitrate_profile, throughput_estimator):
    stime = time.time()

    buffer_length, video_duration, current_cursor = parse_buffer_status(events)

    total_lengths = [int(vduration / 5.0) + 1 for vduration in video_duration]

    cursor_idx = int(current_cursor / 5.0) + 1

    nchunk = 5
    nvideos = 5


    total_reward = -100000000

    max_buffer_idx = -2
    max_bitrate_idx = -2

    buffer_idx = 0
    # for buffer_idx in range(buffer_range_high):
    ret = [-2, -2, -2, -2, -2]
    # in case the buffer is already full
    if buffer_length[buffer_idx] == total_lengths[buffer_idx]:
        return ret

    combo_reward = -100000000

    total_chunk = min(total_lengths[0] - buffer_length[0], 5)

    playlist = [0, 0, 0, 0, 0, 1.0]
    playlist[0] = total_chunk

    bs_info = [0] * total_chunk

    CHUNK_COMBO_OPTIONS = CHUNK_COMBO_OPTIONS_ALL[total_chunk]

    for full_combo in CHUNK_COMBO_OPTIONS:
        combo_info = full_combo

        if combo_info[0] == 0:
            tmp = 1

        reward = computeReward_entry(
            bs_info,
            combo_info,
            playlist,
            bitrate_profile,
            throughput_estimator,
            buffer_length,
            total_lengths,
            current_cursor,
        )

        if reward > combo_reward:
            combo_reward = reward
            max_bitrate_idx = combo_info[0]

    ret[0] = max_bitrate_idx
    if max_bitrate_idx < 0:
        tmp = 1
    return ret

