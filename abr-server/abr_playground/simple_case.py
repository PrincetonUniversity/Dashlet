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

# abs_30 = 1000000000000
# abs_50 = 1000000000000
# abs_70 = 1000000000000


# idx_30 = 0
# idx_50 = 0
# idx_70 = 0

# for i in range(90, 700):
#
#     tk = get_g_with_lambda(i/100)
#     print(tk[1])
#
#     if abs(tk[1] - 0.30) < abs_30:
#         abs_30 = abs(tk[1] - 0.30)
#         idx_30 = i
#
#     if abs(tk[1] - 0.50) < abs_50:
#         abs_50 = abs(tk[1] - 0.50)
#         idx_50 = i
#
#     if abs(tk[1] - 0.70) < abs_70:
#         abs_70 = abs(tk[1] - 0.70)
#         idx_70 = i

idx_70 = 94
idx_50 = 214
idx_30 = 563

print(idx_30)
print(idx_50)
print(idx_70)

g_70, est_seconds = get_g_with_lambda(idx_70 / 100)
g_50, est_seconds = get_g_with_lambda(idx_50 / 100)
g_30, est_seconds = get_g_with_lambda(idx_30 / 100)



g1 = [0.001 for i in range(1001)]
k = -1.6 / 1000000
g2 = [0.0016 + k * i for i in range(1001)]

k = -0.6 / 1000000
g3 = [0.0006 + k * i for i in range(1001)]


# g_func = g_70

def func(x, g_arr):
    if x <= 5:
        idx_max = int(x * 2 * 100)

        sum = 0
        for i in range(idx_max):
            sum += ((2 * x - i / 100) * g_arr[i])

        return sum

    else:

        sum = 0
        for i in range(500):
            sum += ((2 * x - i / 100) * g_arr[i])

        sum += (x - 5)

        for i in range(500, 1000):
            sum += ((x + 5 - i / 100) * g_arr[i])

        return sum

def func2(x, g_arr):

    if x <= 2.5:
        idx_max = int(x * 100)

        sum = 0
        for i in range(idx_max):
            sum += ((x - i / 100) * g_arr[i])

        return sum

    else:

        sum = 0
        for i in range(500):
            if (3 * x - i / 100 - 5) < 0:
                break
            sum += ((3 * x - i / 100 - 5) * g_arr[i])

        for i in range(500, 1000):
            sum += ((2 * x - 5) * g_arr[i])

        return sum

# def plot_rebuffer_penalty(g_arr, filename):
#     x_arr = []
#     p_arr = []
#     p_arr2 = []
#     for idx in range(10, 100):
#         x = idx / 10
#
#         x_arr.append(x)
#         p = func(x, g_arr)
#         p2 = func2(x, g_arr)
#
#         p_arr.append(p)
#         p_arr2.append(p2)
#
#
#     plt.figure(figsize=(6,3))
#
#     plt.plot(x_arr, p_arr, label="(s12, s21, s22)")
#     plt.plot(x_arr, p_arr2, label="(s21, s12, s22)")
#     plt.xlabel("Time to download a 5 second chunk (s)")
#     plt.ylabel("Expected rebuffering penalty")
#     plt.grid()
#     plt.legend()
#     plt.savefig(f"{filename}.png", bbox_inches="tight")
#     plt.close()


def plot_rebuffer_penalty2(g_arr, filename, t_second):
    x_arr = []
    p_arr = []
    p_arr2 = []

    for idx in range(6, 21):

        t = 5 / (idx / 10)

        # x = idx / 10

        x_arr.append(idx / 10)
        p = func(t, g_arr)
        p2 = func2(t, g_arr)

        p_arr.append(p)
        p_arr2.append(p2)


    plt.figure(figsize=(6,3))

    plt.plot(x_arr, p_arr, label="(s12, s21, s22)", linewidth = 3)
    plt.plot(x_arr, p_arr2, label="(s21, s12, s22)", linewidth = 3, linestyle="--")
    plt.xlabel("Network throughput / bitrate")
    plt.ylabel("Expected rebuffer penalty")
    plt.grid()
    plt.title(f"Expect swipe time for s1: {t_second} seconds")
    plt.legend()
    plt.savefig(f"{filename}.png", bbox_inches="tight")
    plt.close()


plot_rebuffer_penalty2(g_70, "result70", 7)
plot_rebuffer_penalty2(g_50, "result50", 5)
plot_rebuffer_penalty2(g_30, "result30", 3)

# plot_rebuffer_penalty(g_arr, filename)
# plot_rebuffer_penalty(g_arr, filename)
# x_tics = [i / 100 for i in range(1001)]
# g2[-1] = 1 - sum(g2[0:1000])
#
# g1_sum = [sum(g1[(i*50+1):((i+1)*50+1)]) for i in range(20)]
# g2_sum = [sum(g2[(i*50+1):((i+1)*50+1)]) for i in range(20)]
#
# plt.plot(g1_sum)
# plt.plot(g2_sum, label="(s21, s12, s22)")
#
#
#
# plt.savefig("dis.png")
# plt.close()


