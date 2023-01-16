import copy

from scipy.signal import savgol_filter


import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 30})

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
g_50, est_seconds = get_g_with_lambda(idx_50 / 100)
g_30, est_seconds = get_g_with_lambda(idx_30 / 100)

g_301, est_seconds = get_g_with_lambda(300 / 100)

dis_70 = copy.deepcopy(g_70)
dis_50 = copy.deepcopy(g_50)


g_70_2 = np.convolve(g_70, g_301)

for i in range(1, len(g_70)):
    g_70[i] += g_70[i-1]
    g_50[i] += g_50[i-1]

for i in range(1, len(g_70_2)):
    g_70_2[i] += g_70_2[i-1]

penalty_s21 = [0 for i in range(len(g_70))]
penalty_s22 = [0 for i in range(len(g_70))]
penalty_s12 = [0 for i in range(len(g_70))]

penalty_s32 = [0 for i in range(len(g_70))]
penalty_s31 = [0 for i in range(len(g_70))]


x_idx = [i / 100 for i in range(1001)]
y_val = [0 for i in range(1001)]

remaining_value1 = 1 - g_70[500]
remaining_value2 = 1 - g_50[500]
remaining_value3 = 1 - g_70[500]

for i in range(500, 1001):
    y_val[i] = remaining_value1

cdf_by_far = 0
for i in range(1, len(g_70)):
    penalty_s21[i] = penalty_s21[i-1] + g_70[i] * 0.01
    penalty_s31[i] = penalty_s31[i-1] + g_70_2[i] * 0.01

for i in range(500, 1001):
    penalty_s22[i] = penalty_s21[i-500] * remaining_value2
    penalty_s32[i] = penalty_s31[i-500] * remaining_value3

for i in range(500, len(g_70)):

    penalty_s12[i] = (i / 100 - 5) * remaining_value1

plt.figure(figsize=(10, 7))
# plt.plot(x_idx, penalty_s12, color=(1, 0, 0), linewidth=5, label="V12")
# plt.plot(x_idx, penalty_s21, color=(1, 0.59765625, 0), linewidth=5, label="V21")
plt.plot(x_idx, penalty_s22, color=(0, 1, 0), linewidth=5, label="V22")
plt.plot(x_idx, penalty_s31, color=(0.2890625, 0.5234375, 0.90625), linewidth=5, label="V31")
# plt.plot(x_idx, penalty_s32, color=(1, 0, 1), linewidth=5, label="V32")
plt.ylim([0, 3.5])
# plt.ylabel("Expected rebuffering penalty")
plt.legend(loc='upper left', bbox_to_anchor=(0.05, 1.0), ncol=2)
# plt.axis('off')
plt.savefig("all-rebuffer-s21.png", bbox_inches='tight')
plt.close()

####################################################################

# g_50, g_70

def plot_distribution(pname, data, linecolor):
    out = []
    x = []

    for i in range(10):
        d = np.sum(data[(1+100*i):(1+100*(i+1))])

        out.append(d * 10)
        x.append(i + 0.5)
    plt.figure(figsize=(3, 2))
    plt.bar(x, out, color=linecolor)
    plt.xlim([0, 10])
    plt.ylim([0, 7])
    plt.xlabel("Time (s)")
    # plt.ylabel("Swipe time distribution")
    plt.axis("off")
    plt.savefig(f"./plot/{pname}.png", bbox_inches='tight')

    plt.close()
    tmp = 1


def plot_distribution2(pname, data, linecolor):
    out = [0] * 25
    x = [i + 0.5 for i in range(25)]

    for i in range(25):

        if 1+100*(i+1) <= len(data):
            d = np.sum(data[(1+100*i):(1+100*(i+1))])

            out[i] = d * 10

    plt.figure(figsize=(6, 2))
    plt.bar(x, out, color=linecolor)
    plt.xlim([0, 25])
    plt.ylim([0, 7])
    plt.xlabel("Time (ss)")
    # plt.ylabel("Swipe time distribution")
    plt.axis("off")
    plt.savefig(f"./plot/{pname}.png", bbox_inches='tight')

    plt.close()
    tmp = 1

# dis_70 = savgol_filter(dis_70, 201, 3)

plot_distribution("g1", dis_70, "r")
plot_distribution("g2", dis_50, "b")

p12 = [0] * 2501
p12[501] = remaining_value1

p21 = dis_70

p22 = [0] * 500

for i in range(len(p21)):
    p22.append(p21[i] * remaining_value2)

p32 = [0] * 500

p31 = np.convolve(dis_70, dis_50)
for i in range(len(p31)):
    p32.append(p31[i] * remaining_value3)

plot_distribution2("p12", p12, (1, 0, 0))
plot_distribution2("p21", p21, (1, 0.59765625, 0))
plot_distribution2("p22", p22, (0, 1, 0))
plot_distribution2("p31", p31, (0.2890625, 0.5234375, 0.90625))
plot_distribution2("p32", p32, (1, 0, 1))



# plt.plot(x_idx, penalty_s12, color=(1, 0, 0), linewidth=4, label="S12")
# plt.plot(x_idx, penalty_s21, color=(1, 0.59765625, 0), linewidth=4, label="S21")
# plt.plot(x_idx, penalty_s22, color=(0, 1, 0), linewidth=4, label="S22")
# plt.plot(x_idx, penalty_s31, color=(0.2890625, 0.5234375, 0.90625), linewidth=4, label="S31")
# plt.plot(x_idx, penalty_s32, color=(1, 0, 1), linewidth=4, label="S32")


tmp = 1