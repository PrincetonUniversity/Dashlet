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


for i in range(1, len(g_70)):
    g_70[i] += g_70[i-1]


plt.figure(figsize=(10, 3))
plt.plot(g_70, color="k", linewidth=4)

# plt.plot([1001, 1201], [1, 1], color="k", linewidth=3)
plt.fill_between([i for i in range(300)], g_70[:300], linewidth=4, color=(0.85, 0.92, 0.83))
plt.axis('off')
plt.ylim([0, 1])
plt.savefig("rebuffer-s21-1.png", bbox_inches='tight')
plt.close()

plt.figure(figsize=(10, 3))
plt.plot(g_70, color="k", linewidth=4)

# plt.plot([1001, 1201], [1, 1], color="k", linewidth=3)
plt.fill_between([i for i in range(600)], g_70[:600], linewidth=4, color=(0.85, 0.92, 0.83))

# plt.fill_between([1001, 1201], [1, 1], linewidth=3, color=(0.85, 0.92, 0.83))
plt.axis('off')
plt.ylim([0, 1])
plt.savefig("rebuffer-s21-2.png", bbox_inches='tight')
plt.close()


x_idx = [i for i in range(1001)]
y_val = [0 for i in range(1001)]

remaining_value = 1 - g_70[500]

for i in range(500, 1001):
    y_val[i] = remaining_value

plt.figure(figsize=(10, 3))
plt.plot(x_idx, y_val, color="k", linewidth=4)
plt.plot([0, 1001], [1, 1], color="k", linewidth=4, linestyle="--")
plt.axis('off')
plt.savefig("rebuffer-s12-1.png", bbox_inches='tight')
plt.close()

plt.figure(figsize=(10, 3))
plt.plot(x_idx, y_val, color="k", linewidth=4)
plt.plot([0, 1001], [1, 1], color="k", linewidth=4, linestyle="--")
plt.fill_between(x_idx[500:600], y_val[500:600], linewidth=4, color=(0.79, 0.85, 0.97))
plt.axis('off')
plt.savefig("rebuffer-s12-2.png", bbox_inches='tight')
plt.close()


tmp = 1




# color=(0.85, 0.92, 0.83)
# color=(0.79, 0.85, 0.97)






