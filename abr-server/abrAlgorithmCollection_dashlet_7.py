#!/usr/bin/env python

import base64
import copy
import urllib
import sys
import os
import json

import numpy as np
import time
import itertools
from itertools import permutations
import math

stime = time.time()


bitraterewards = [1143, 2064, 4449, 6086, 9193, 0]
chunklength = 7.00

penalty_weight = 700000

buffer_threshold = bitraterewards[0] / penalty_weight


def to_chunk_idx(ts, chunk_size):
    return math.floor(ts / chunk_size - 0.0000000001)


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

    last_quality = []

    for i in range(len(events)):
        event = events[i]

        idx = event["lastRequest"] + 1

        buffer_length.append(idx)

        video_duration.append(event["duration"])
        last_quality.append(event["lastquality"])

    # total buffered video in seconds - not played video in the buffer
    current_cursor = min(buffer_length[0] * 7, video_duration[0]) - events[0]["buffer"]

    return buffer_length, video_duration, last_quality, current_cursor



def dash_sv(events, probability_weights, bitrate_profile, estimate_throughput):
    stime = time.time()

    ret = [-2, -2, -2, -2, -2]

    buffer_length, video_duration, last_quality, current_cursor = parse_buffer_status(events)

    look_forward_time = 25
    danger_zone_time = 5

    total_lengths = [int((vduration - 0.00000001)/ 7.0) + 1 for vduration in video_duration]

    cursor_idx = int(current_cursor / 7.0) + 1

    current_playback_ts = int(current_cursor)

    update_weights = copy.deepcopy(probability_weights)

    update_weights[0] = update_weights[0][current_playback_ts:] / np.sum(update_weights[0][current_playback_ts:])

    nvideos = 5

    head_distribution = [np.array([1.0]) for i in range(nvideos)]

    for i in range(1, nvideos):
        head_distribution[i] = np.convolve(head_distribution[i-1], update_weights[i-1])

    total_distribution = {}

    danger_zone_dict = {}

    candidate_high = copy.deepcopy(buffer_length)

    for i in range(nvideos):
        for j in range(buffer_length[i], total_lengths[i]):
            if i == 0:
                shift_distance = j * int(chunklength) - int(current_cursor)
            else:
                shift_distance = j * int(chunklength)
            shift_array = np.array([0.0 for ai in range(shift_distance)])

            total_distribution[(i, j)] = np.concatenate((shift_array, head_distribution[i])) * np.sum(update_weights[i][shift_distance:])


            this_penalty = 0
            danger_penalty = 0
            for tidx in range(min(look_forward_time, len(total_distribution[(i, j)]))):
                this_penalty += (look_forward_time - tidx) * total_distribution[(i, j)][tidx]

            for tidx in range(min(danger_zone_time, len(total_distribution[(i, j)]))):
                danger_penalty += (danger_zone_time - tidx) * total_distribution[(i, j)][tidx]

            if this_penalty > buffer_threshold:
                candidate_high[i] = j + 1

            if danger_penalty > buffer_threshold:
                danger_zone_dict[(i, j)] = 1

            # print((i, j, this_penalty))

    candidate_num = 0
    for i in range(nvideos):
        candidate_num += (candidate_high[i] - buffer_length[i])

    if candidate_num == 0:
        return ret

    target_bitrate = look_forward_time * estimate_throughput / candidate_num

    max_penalty = 0
    max_buffer_i = 0

    for i in range(nvideos):
        j = buffer_length[i]

        if (i, j) not in total_distribution.keys():
            continue

        look_forward_local = max(int(look_forward_time * 2 / candidate_num) + 1, 10)

        this_penalty = 0
        for tidx in range(min(look_forward_local, len(total_distribution[(i, j)]))):
            this_penalty += (look_forward_local - tidx) * total_distribution[(i, j)][tidx]

        if max_penalty < this_penalty:
            max_penalty = this_penalty
            max_buffer_i = i

    max_buffer_j = buffer_length[max_buffer_i]


    if (max_buffer_i, max_buffer_j) in danger_zone_dict.keys():
        target_bitrate /= 2

    bitrate_choice = 0

    if max_penalty < 0.00001:
        return ret

    for i in range(1, len(bitrate_profile[max_buffer_i][max_buffer_j])):
        # chunk_duration = min(chunklength, video_duration[max_buffer_i] - max_buffer_j * chunklength)

        # print("=====================")
        # print(bitrate_profile[max_buffer_i][max_buffer_j][i] / chunklength)
        # print(target_bitrate)

        if bitrate_profile[max_buffer_i][max_buffer_j][i] < target_bitrate:
            bitrate_choice = i

    # Take care of smoothness, reduce the bitrate to align with the formal chunk
    if last_quality[max_buffer_i] != -1:
        if bitrate_choice != (len(bitrate_profile[max_buffer_i][max_buffer_j]) - 1):
            bitrate_choice = last_quality[max_buffer_i]

    # if bitrate_choice != (len(bitrate_profile[max_buffer_i][max_buffer_j]) - 1):
    #     print("change")
    ret[max_buffer_i] = bitrate_choice

    return ret

    # 5 second danger zone
    # 10 second first chunk observe zone




def oracle_sv(events, probability_weights, bitrate_profile, throughput_estimate):
    stime = time.time()

    ret = [-2, -2, -2, -2, -2]

    buffer_length, video_duration, last_quality, current_cursor = parse_buffer_status(events)

    look_forward_time = 25

    look_ahead_chunks = to_chunk_idx(look_forward_time, chunklength) + 1

    cur_cidx = to_chunk_idx(current_cursor, chunklength) + 1

    begin_chunks = [0 for i in range(5)]

    begin_chunks[0] = cur_cidx

    watche_seconds = []

    for i in range(5):
        idx = 0
        for j in range(len(probability_weights[i])):

            if probability_weights[i][j] > 0.999:
                idx = j
                break

        watche_seconds.append(idx + 0.5)

    watch_chunks_per_video = [to_chunk_idx(watche_seconds[i], chunklength) + 1 for i in range(5)]


    watch_start_time = {}
    watch_start_time[(0, 0)] = 0

    for j in range(1, watch_chunks_per_video[0]):
        watch_start_time[(0, j)] = watch_start_time[(0, j-1)] + chunklength

    for i in range(1, 5):
        watch_start_time[(i, 0)] = watch_start_time[(i-1, 0)] + watche_seconds[i-1]

        for j in range(1, watch_chunks_per_video[i]):
            watch_start_time[(i, j)] = watch_start_time[(i, j-1)] + chunklength


    watch_list = []
    download_list = []

    bitrate_options = []

    for i in range(5):
        for j in range(begin_chunks[i], watch_chunks_per_video[i]):

            if len(watch_list) < look_ahead_chunks:
                watch_list.append((i, j))
            else:
                break

    for entry in watch_list:
        vid = entry[0]
        cid = entry[1]

        if cid >= buffer_length[vid]:
            download_list.append(entry)

            bitrate_options.append([i for i in range(len(bitrate_profile[vid][cid]))])

    if len(download_list) == 0:
        return ret

    bitrate_choices = itertools.product(*bitrate_options)

    max_reward = -1000000000000.0
    max_choice = (-2, -2, -2, -2, -2)

    for bitrate_choice in bitrate_choices:
        # print(bitrate_choice)

        download_size = []

        bitrate_diff = []

        bitrate_record = {}
        if download_list[0][1] != 0:
            bitrate_record[(download_list[0][0], download_list[0][1] -1)] = events[download_list[0][0]]['lastquality']


        smoothness_penalty = 0

        bitrate_reward = 0

        for seqi in range(len(download_list)):
            vid = download_list[seqi][0]
            cid = download_list[seqi][1]
            bitrate_idx = bitrate_choice[seqi]

            bitrate_record[(vid, cid)] = bitrate_idx

            download_size.append(bitrate_profile[vid][cid][bitrate_idx])

            bitrate_reward += bitrate_profile[vid][cid][bitrate_idx]

            if cid != 0:
                pre_bitrate_idx = bitrate_record[(vid, cid-1)]
                smoothness_penalty += abs(bitrate_profile[vid][cid-1][bitrate_idx] - bitrate_profile[vid][cid-1][pre_bitrate_idx]) / chunklength

        for i in range(1, len(download_size)):
            download_size[i] += download_size[i-1]

        download_time = [download_size[i] / throughput_estimate for i in range(len(download_size))]

        # throughput_estimator.timeToDownload(download_size)

        total_rebuffer = 0

        for i in range(len(download_list)):
            rebuffer = max(0, download_time[i] + 7 - (watch_start_time[download_list[i]] + total_rebuffer))

            total_rebuffer += rebuffer

        reward = bitrate_reward - smoothness_penalty * 4.3 / 2 - penalty_weight * 4.3 * total_rebuffer

        if reward > max_reward:
            max_reward = reward
            max_choice = bitrate_choice

    ret[download_list[0][0]] = max_choice[0]

    return ret

