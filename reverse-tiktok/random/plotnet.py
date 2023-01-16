import matplotlib.pyplot as plt
import numpy as np

def load_network(filename):
    data = np.loadtxt(filename)

    ret = [0] * int(data[-1] / 1000 + 1)

    for i in range(len(data)):
        ret[int(data[i]/1000)] += 1

    for i in range(len(ret)):

        ret[i] = ret[i] * 1500 * 8 / 1000 / 1000

    return ret

for i in range(13):

    data = load_network(f"../traces/network/wifi-{i}.down")

    print(np.average(data))
    plt.plot(data)
    plt.savefig(f"{i}.png")
    plt.close()