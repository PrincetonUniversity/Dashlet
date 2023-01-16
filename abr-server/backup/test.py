import itertools
import numpy as np
import matplotlib.pyplot as plt

def sampling(lamda, time, portion):

    nlen = int(time) + 1

    ret = [0 for i in range(nlen)]

    for i in range(nlen - 1):
        ret[i] = portion * ((1 - np.exp(-1 * lamda * (i + 1) / time)) - (1 - np.exp(-1 * lamda * i / time)))

    ret[-1] = 1 - sum(ret)

    return ret



def get_swipe_dis_by_id(time, target_rates):

    lamda = 1.0/ target_rates

    dis = sampling(lamda, time, 0.9)

    return dis

dis = get_swipe_dis_by_id(9, 9/10)

plt.plot(dis)
plt.show()
plt.close()

