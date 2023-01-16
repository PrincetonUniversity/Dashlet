# blocklist = [0, 7, 14, 21, 27, 34]
# blocklist = [0, 6, 12, 17, 23, 29, 34]
# blocklist = [0, 5, 10, 15, 20, 25, 30, 35]


import numpy as np

data = np.loadtxt("wifi-9.down")


def getblocklist(tp):

    gap = 8.8 / tp

    blist = []

    tmp = 0

    for i in range(100):

        if tmp > gap:
            blist.append(i)
            tmp -= gap

        tmp += 1

    return blist



for nid in range(1, 7):
    blocklist = getblocklist(nid)
    output = []
    for i in range(len(data)):
        if i % 100 in blocklist:
            output.append(data[i])


    np.savetxt(f"wifi-{nid + 19}.down", output, fmt="%d")


