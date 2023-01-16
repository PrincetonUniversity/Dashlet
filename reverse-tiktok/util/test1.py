import json
import time
import itertools

import numpy as np


import matplotlib.pyplot as plt
import random
from statsmodels.distributions.empirical_distribution import ECDF
from matplotlib.patches import Rectangle


cmap = plt.get_cmap('viridis')
cmaplist = [cmap(i) for i in range(cmap.N)]


bitrate_map = {}

CHUNK_COMBO_OPTIONS = []

for combo in itertools.product([1,2], repeat=3):
    CHUNK_COMBO_OPTIONS.append(combo)

for i in range(len(CHUNK_COMBO_OPTIONS)):
    bitrate_map[CHUNK_COMBO_OPTIONS[i]] = cmaplist[i*32]

chunk_size = 5
bit_rate = 1

order_map = {}
order_map[0] = cmaplist[0]
order_map[1] = cmaplist[128]
order_map[2] = cmaplist[255]


def draw_bar(ax, pos_i, pos_j, reward_list, color_map):

    max_reward = reward_list[0][0]

    for i in range(len(reward_list)):

        if abs(reward_list[i][0] - max_reward) < 0.000001:

            loc_i = pos_i * 15 + 5 * (i % 2)

            loc_j = pos_j * 15 + 5 * (i // 2)

            ax.add_patch(Rectangle((loc_i, loc_j), 5, 5, color=color_map[reward_list[i][1]]))

    # ax.add_patch(Rectangle((start, i), 5, 5, color=barcolor))


def draw_bar_order(ax, pos_i, pos_j, reward_list, color_map):

    max_reward = reward_list[0][0]

    for i in range(len(reward_list)):

        if abs(reward_list[i][0] - max_reward) < 0.000001:

            loc_i = pos_i * 15 + 5 * (i % 2)

            loc_j = pos_j * 15 + 5 * (i // 2)

            ax.add_patch(Rectangle((loc_i, loc_j), 5, 5, color=color_map[reward_list[i][2]]))

    # ax.add_patch(Rectangle((start, i), 5, 5, color=barcolor))

def evaluate(p, throughput, sequence):

    seqidx = 0
    for i in range(3):
        if sequence[i] == 0:
            seqidx = i

    CHUNK_COMBO_OPTIONS = []

    for combo in itertools.product([1,2], repeat=3):
        CHUNK_COMBO_OPTIONS.append(combo)

    qoe_list = []

    for bit_rate_choice in CHUNK_COMBO_OPTIONS:

        dtime = [0 for i in range(3)]

        for i in range(len(sequence)):
            dtime[sequence[i]] = (i + 1) * (chunk_size * bit_rate_choice[i] / throughput)

        viewtime = [{0: 5}, {1: 2.5}, {1: 2.5, 2: 5}]

        prob = [1-p, p*(1-p), p*p]

        penalty = 0
        reward = 0
        for i in range(3):

            viewlist = viewtime[i]

            rebuffer_time = 0
            cur_reward = 0

            for key in viewlist:

                rebuffer_time += max(dtime[key] - (viewlist[key] + rebuffer_time), 0)

                cur_reward += bit_rate_choice[key]

            penalty += (rebuffer_time * prob[i])
            reward += (cur_reward * prob[i])

        qoe = reward - 2 * penalty


        qoe_list.append([qoe, bit_rate_choice, seqidx])

    return qoe_list


probs = [i / 10 for i in range(10)]
throughputs = [i / 2 for i in range(1, 16)]


result = [[0 for j in range(16)] for i in range(10)]

for i in range(10):
    for j in range(1, 16):

        penalty_list = []

        penalty = evaluate(i / 10, j / 2, [0, 1, 2])
        penalty_list.extend(penalty)

        penalty = evaluate(i / 10, j / 2, [1, 0, 2])
        penalty_list.extend(penalty)

        penalty = evaluate(i / 10, j / 2, [1, 2, 0])
        penalty_list.extend(penalty)

        penalty_list = sorted(penalty_list, reverse=True)
        # idx = np.argmax(penalty_list)

        # if i == 8 and j == 3:
        #     tmp = 1

        result[i][j] = penalty_list[0:4]

tmp = 1



print(result)

plt.figure(figsize=(10, 10))
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

for i in range(10):
    for j in range(1, 16):
        draw_bar(ax, i, j, result[i][j], bitrate_map)


for i in range(8):
    ax.add_patch(Rectangle((10*16-10, i*10 + 20), 5, 5, color=bitrate_map[CHUNK_COMBO_OPTIONS[i]]))
    ax.text(10*16, i*10 + 20, str(CHUNK_COMBO_OPTIONS[i]))


ax.set_xlim(0 - 5, 10*16 - 10 + 35)
ax.set_ylim(15 - 5, 15*16 + 5)

plt.xticks([5 + i * 15 for i in range(10)], [f"{(i/10):.1f}" for i in range(10)])
plt.yticks([5 + i * 15 for i in range(1, 16)], [f"{(i/2):.1f}" for i in range(1, 16)])



plt.xlabel("Swipe probability")
plt.ylabel("Network throughput / Video Bitrate 1")

plt.savefig("bitrate.png", bbox_inches='tight')
plt.close()




plt.figure(figsize=(10, 10))
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

for i in range(10):
    for j in range(1, 16):
        draw_bar_order(ax, i, j, result[i][j], order_map)

order_list = ["0, 1, 2", "1, 0, 2", "1, 2, 0"]

for i in range(3):
    ax.add_patch(Rectangle((10*16-10, i*10 + 20), 5, 5, color=order_map[i]))
    ax.text(10*16, i*10 + 20, order_list[i])

ax.set_xlim(0 - 5, 10*16 - 10 + 35)
ax.set_ylim(15 - 5, 15*16 + 5)

plt.xticks([5 + i * 15 for i in range(10)], [f"{(i/10):.1f}" for i in range(10)])
plt.yticks([5 + i * 15 for i in range(1, 16)], [f"{(i/2):.1f}" for i in range(1, 16)])

plt.xlabel("Swipe probability")
plt.ylabel("Network throughput / Video Bitrate 1")

plt.savefig("order.png", bbox_inches='tight')
plt.close()