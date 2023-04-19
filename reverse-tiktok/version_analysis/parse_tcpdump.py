import matplotlib.pyplot as plt
import numpy as np

from matplotlib.patches import Rectangle

plt.rcParams.update({'font.size': 23})
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
throughput_dict_up = {}
throughput_dict_down = {}

IDX_TIME = 1
IDX_SRC = 2
IDX_DST = 4
IDX_BYTES = 6


def draw_rebuffer(ax, start, end):
    ax.add_patch(Rectangle((start, 0), end-start, 100, color=(181/255, 181/255, 181/255)))

def get_arr(fname):

    data_arr = [0] * 10000

    with open(fname) as fd:

        for line in fd.readlines():
            parseline = line.strip()
            items = parseline.split()

            # print(parseline)

            # print((items[IDX_TIME], items[IDX_SRC], items[IDX_DST], items[IDX_BYTES]))

            # if "192.168.1.3" == items[IDX_SRC]:
            #     if items[IDX_DST] not in throughput_dict_up.keys():
            #         throughput_dict_up[items[IDX_DST]] = 0
            #     throughput_dict_up[items[IDX_DST]] += int(items[IDX_BYTES].strip("(").strip(")"))
            #
            # else:
            #     if items[IDX_SRC] not in throughput_dict_down.keys():
            #         throughput_dict_down[items[IDX_SRC]] = 0
            #
            #     throughput_dict_down[items[IDX_SRC]] += int(items[IDX_BYTES].strip("(").strip(")"))

            if "192.168.1.3" == items[IDX_SRC] and  "192.168.1.2" == items[IDX_DST]:
                data_arr[int(float(items[IDX_TIME]))] += int(items[IDX_BYTES])
    return data_arr

data_arr = get_arr("parsed10-v20.9.txt")
data_arr = data_arr[300:600]
data_arr1 = get_arr("parsed10-v26.3.txt")
data_arr1 = data_arr1[300:600]


grey_arr = [0] * len(data_arr)

for i in range(0, len(data_arr)):

    if (data_arr[i] > 1000 and data_arr1[i] > 1000):
        grey_arr[i] = 1

for i in range(0, len(data_arr)):
    data_arr[i] += data_arr[i-1]

for i in range(0, len(data_arr1)):
    data_arr1[i] += data_arr1[i-1]



for i in range(0, len(data_arr)):
    data_arr[i] /= 1000000

for i in range(0, len(data_arr1)):
    data_arr1[i] /= 1000000


# plt.figure()
fig, ax = plt.subplots(figsize=(8, 3))

startx = -1

# for i in range(len(grey_arr)):
#     if grey_arr[i] == 1 and startx == -1:
#         startx = i
#
#     if grey_arr[i] == 0 and startx != -1:
#         draw_rebuffer(ax, startx, i)
#         startx = -1
#
# if startx != -1:
#     draw_rebuffer(ax, startx, len(grey_arr))


for i in range(len(data_arr)):
    data_arr[i] -= int (data_arr[i] / 20) * 20
    data_arr1[i] -= int(data_arr1[i] / 20) * 20


plt.plot(data_arr, "b-.", linewidth="2", label="TikTok V20")
plt.plot(data_arr1, "r--", linewidth="2", label="TikTok V26")

plt.xlabel("Time (s)")
plt.ylabel("Cumulative download\ndata modulo 20 (MB) ")
# plt.ylim([0, 24])
plt.grid()
plt.ylim([0, 27])
plt.legend(ncol=2, loc=(0.05, 0.75))
plt.savefig("download-trace-version.pdf", bbox_inches='tight')
plt.close()
