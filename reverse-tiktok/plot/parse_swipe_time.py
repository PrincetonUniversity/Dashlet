import csv
import numpy as np
import matplotlib.pyplot as plt
import random
from statsmodels.distributions.empirical_distribution import ECDF

plt.rcParams.update({'font.size': 18})




fname = "../data/tt-5-mid/tt-5-mid-swipe-time.log"

def get_swipe_gap(fname):

    data = np.loadtxt(fname)

    swipe_list = []
    gap_list = []
    for d_entry in data:

        if d_entry[2] - d_entry[5] > 150 and abs(d_entry[2] - d_entry[5]) > abs(d_entry[4] - d_entry[1]):
            swipe_list.append(d_entry[0])


    for i in range(1, len(swipe_list)):
        gap_list.append(swipe_list[i] - swipe_list[i-1])

    return gap_list


final_list = []

for net in ["low", "mid", "high"]:
    for uid in range(3, 11):
        fname = f"../data/tt-{uid}-{net}/tt-{uid}-{net}-swipe-time.log"

        final_list.extend(get_swipe_gap(fname))



plt.figure(figsize=(8,6))
ecdf_effect_download = ECDF(final_list)

plt.plot(ecdf_effect_download.x, ecdf_effect_download.y, lw=3)
# plt.legend()
plt.grid()
# plt.show()
plt.ylabel("CDF")
plt.xlabel("Video watch time (s)")
plt.xlim([0, 60])
plt.savefig("watch-time-tt.png", bbox_inches='tight')
plt.close()



#     print(d_entry[3] - d_entry[0], d_entry[4] - d_entry[1], d_entry[5] - d_entry[2])
# tmp = 1

