import matplotlib.pyplot as plt


g1 = [0.001 for i in range(1001)]
k = -1.6 / 1000000
g2 = [0.0016 + k * i for i in range(1001)]

k = -0.6 / 1000000
g3 = [0.0006 + k * i for i in range(1001)]

print(sum(g1))

g_func = g3

def func(x):
    idx_max = min(int(x * 2 * 100), 1000)

    sum = 0

    for i in range(idx_max):
        for j in range(idx_max):

            if (2 * x - (i + j) / 100) < 0 or (10 - (i + j) / 100)< 0:
                break

            sum += ((2 * x - (i + j) / 100) * g_func[i] * g_func[j])

    if x - 5 > 0:

        for i in range(500, 1000):

                sum += ((x - 5) * g_func[i])
    return sum

def func2(x):
    idx_max = int(x * 100)
    sum = 0

    for i in range(idx_max):
        for j in range(idx_max):

            if (x - (i + j) / 100) < 0:
                break

            sum += ((x - (i + j) / 100) * g_func[i] * g_func[j])

    if 2 * x - 5 > 0:

        for i in range(500, 1000):

            sum += ((2 * x - 5) * g_func[i])

    return sum


x_arr = []
p_arr = []
p_arr2 = []
for idx in range(10, 100):
    x = idx / 10

    x_arr.append(x)
    p = func(x)
    p2 = func2(x)

    p_arr.append(p)
    p_arr2.append(p2)

plt.plot(x_arr, p_arr, label="(s12, s31, s22, s32)")
plt.plot(x_arr, p_arr2, label="(s31, s21, s22, s32)")
plt.xlim([0, 5])
plt.ylim([0, max(p_arr[40], p_arr2[40])])
plt.xlabel("Time to download a 5 second chunk")
plt.ylabel("Expected rebuffering penalty")
plt.grid()
plt.legend()
plt.savefig("result_skip.png", bbox_inches="tight")
plt.close()


x_tics = [i / 2 for i in range(1, 21)]
g2[-1] = 1 - sum(g2[0:1000])
g3[-1] = 1 - sum(g3[0:1000])

g1_sum = [sum(g1[(i*50+1):((i+1)*50+1)]) for i in range(20)]
g2_sum = [sum(g2[(i*50+1):((i+1)*50+1)]) for i in range(20)]
g3_sum = [sum(g3[(i*50+1):((i+1)*50+1)]) for i in range(20)]

plt.plot(x_tics, g1_sum)
plt.plot(x_tics, g2_sum)
plt.plot(x_tics, g3_sum)

plt.xlabel("Swipe Time (s)")
plt.ylabel("Power density function")



plt.savefig("dis.png")
plt.close()


