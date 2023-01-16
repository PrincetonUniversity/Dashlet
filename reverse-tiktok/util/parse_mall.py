

for trail_idx in range(10):

    fd = open(f"../traces/mall/bbw-{trail_idx}.txt")

    data = fd.readlines()

    fd.close()

    data_arr = []

    for entry in data:
        items = entry.strip().split()

        val = float(items[6])

        if items[7] == 'Mbits/sec':
            val *= 1000000

        if items[7] == 'Kbits/sec':
            val *= 1000

        data_arr.append(val)


    ofd = open(f"../traces/network/wifi-{trail_idx}.down", "w")

    for cnt, entry in enumerate(data_arr):

        npacket = int(entry / (1500 * 8))

        for i in range(npacket):
            ms = int(i * 1000 / npacket)

            ofd.write(str(cnt * 1000 + ms))
            ofd.write("\n")

    ofd.close()
