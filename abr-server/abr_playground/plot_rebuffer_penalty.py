import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 17})

def get_cdf(lamda, x):
    return 1-np.exp(-1 * lamda * x)

def get_g_with_lambda(lamda):
    g_func = [get_cdf(lamda, i / 1000) for i in range(1001)]

    for i in range(len(g_func) - 1):
        g_func[i] = (g_func[i+1] - g_func[i]) * 0.85

    g_func[-1] = 1 - sum(g_func[0:(len(g_func) - 1)])

    est_seconds = 0

    for i in range(1001):
        est_seconds += i / 1000 * g_func[i]

    return g_func, est_seconds

idx_70 = 94
idx_50 = 214
idx_30 = 563

print(idx_30)
print(idx_50)
print(idx_70)

g_70, est_seconds = get_g_with_lambda(idx_70 / 100)
# g_50, est_seconds = get_g_with_lambda(idx_50 / 100)
# g_30, est_seconds = get_g_with_lambda(idx_30 / 100)

g_70_2 = np.convolve(g_70, g_70)

for i in range(1, len(g_70)):
    g_70[i] += g_70[i-1]

for i in range(1, len(g_70_2)):
    g_70_2[i] += g_70_2[i-1]


penalty_s21 = [0 for i in range(len(g_70))]
penalty_s12 = [0 for i in range(len(g_70))]


x_idx = [i for i in range(1001)]
y_val = [0 for i in range(1001)]

remaining_value = 1 - g_70[500]

for i in range(500, 1001):
    y_val[i] = remaining_value


cdf_by_far = 0
for i in range(1, len(g_70)):

    penalty_s21[i] = penalty_s21[i-1] + g_70[i] * 0.01


for i in range(500, len(g_70)):

    penalty_s12[i] = (i / 100 - 5) * remaining_value


plt.figure(figsize=(10, 3))
plt.plot(penalty_s21, color="k", linewidth=4)
plt.ylim([0, 3.5])
# plt.axis('off')
plt.savefig("t-rebuffer-s21.png", bbox_inches='tight')
plt.close()


plt.figure(figsize=(10, 3))
plt.plot(penalty_s12, color="k", linewidth=4)
plt.ylim([0, 3.5])
# plt.axis('off')
plt.savefig("t-rebuffer-s12.png", bbox_inches='tight')
plt.close()




# plt.figure(figsize=(10, 3))
# plt.plot(g_70, color="k", linewidth=4)
#
# # plt.plot([1001, 1201], [1, 1], color="k", linewidth=3)
# plt.fill_between([i for i in range(300)], g_70[:300], linewidth=4, color=(0.85, 0.92, 0.83))
# plt.axis('off')
# plt.ylim([0, 1])
# plt.savefig("rebuffer-s21-1.png", bbox_inches='tight')
# plt.close()
#
# plt.figure(figsize=(10, 3))
# plt.plot(g_70, color="k", linewidth=4)
#
# # plt.plot([1001, 1201], [1, 1], color="k", linewidth=3)
# plt.fill_between([i for i in range(600)], g_70[:600], linewidth=4, color=(0.85, 0.92, 0.83))
#
# # plt.fill_between([1001, 1201], [1, 1], linewidth=3, color=(0.85, 0.92, 0.83))
# plt.axis('off')
# plt.ylim([0, 1])
# plt.savefig("rebuffer-s21-2.png", bbox_inches='tight')
# plt.close()
#
#
#
#
# plt.figure(figsize=(10, 3))
# plt.plot(x_idx, y_val, color="k", linewidth=4)
# plt.plot([0, 1001], [1, 1], color="k", linewidth=4, linestyle="--")
# plt.axis('off')
# plt.savefig("rebuffer-s12-1.png", bbox_inches='tight')
# plt.close()
#
# plt.figure(figsize=(10, 3))
# plt.plot(x_idx, y_val, color="k", linewidth=4)
# plt.plot([0, 1001], [1, 1], color="k", linewidth=4, linestyle="--")
# plt.fill_between(x_idx[500:600], y_val[500:600], linewidth=4, color=(0.79, 0.85, 0.97))
# plt.axis('off')
# plt.savefig("rebuffer-s12-2.png", bbox_inches='tight')
# plt.close()