import re
import matplotlib.pyplot as plt

# from abr_server.env import chunk

def parse_real(filename):

    uid_dict = {}

    event_dict = {}

    download_time_dict = {}
    
    u_idx = 0

    with open(filename) as f:
        lines = f.read().splitlines()

        for line in lines:
            items = line.split("\t")

            if (items[0] == '[download]'):
                # print(items)

                uid = items[1]
                if uid not in uid_dict.keys():
                    uid_dict[uid] = u_idx

                    u_idx += 1
                
                event_dict[(uid_dict[uid], int(items[2]))] = float(items[5])
                download_time_dict[(uid_dict[uid], int(items[2]))] = float(items[5]) - float(items[4])

    return event_dict, download_time_dict



throughput = parse_real("/home/acer/Documents/ttstream/run/result-sim/empc/10timesaccurate/trace_11736_http---www.ebay.com/36.148.101.219-1.txt")

tmp = 1
# def parse_simu(filename):
#
#     simu_trace = []
#     with open(filename) as f:
#         lines = f.read().splitlines()
#
#         for line in lines:
#             items = line.split(", ")
#
#             if (items[1] == "v"):
#                 # print(items)
#                 simu_trace.append([int(items[2]), int(items[3]), float(items[0])])
#
#     return simu_trace


# real_trace, real_trace_dt = parse_real("../testing/out2.log")
# simu_trace = parse_simu("./simu.log")
#
#
# real_x = []
# simu_y = []
#
# trace = []
#
# for i in range(len(simu_trace)):
#     key = (simu_trace[i][0], simu_trace[i][1])
#     if key in real_trace.keys():
#         real_x.append(real_trace[key])
#         simu_y.append(simu_trace[i][2])
#         trace.append(key)
#         # pass
#     # else:
#         # print(simu_trace[i])
#
#
# real_offset = real_x[0]
# simu_offset = simu_y[0]
#
#
# for i in range(len(real_x)):
#     real_x[i] = (real_x[i] - real_offset) / 1000
#     simu_y[i] -= simu_offset
#
#
#
# print (real_x)
# print (simu_y)
#
#
# plt.scatter(real_x, simu_y)
# plt.plot([0, 240], [0, 240], "k--")
# plt.plot()
# plt.xlabel("Recorded event time (s)" )
# plt.ylabel("Simulate event time (s)" )
# plt.savefig("result.png")
# plt.close()
#
#
# real_dt = []
# simu_dt = []
#
# for i in range(len(simu_trace)):
#     if simu_trace[i][1] == 0:
#         continue
#     key = (simu_trace[i][0], simu_trace[i][1])
#
#     if key in real_trace_dt.keys():
#         simu_dt.append(simu_trace[i][2] - simu_trace[i-1][2])
#         real_dt.append(real_trace_dt[key] / 1000)
#
#
#
# plt.scatter(real_dt, simu_dt)
# plt.plot([0, 30], [0, 30], "k--")
# plt.plot()
# plt.xlabel("Real chunk download time (s)")
# plt.ylabel("Simulate chunk download time (s)")
# plt.savefig("download.png")
# plt.close()
#
# # real_trace_dt
#
# for i in range(1, len(real_x)):
#     r_diff = real_x[i] - real_x[i-1]
#     s_diff = simu_y[i] - simu_y[i-1]
#
#     if r_diff / s_diff > 1.1:
#
#         print((r_diff, s_diff, trace[i], real_trace_dt[trace[i]] / 1000))

