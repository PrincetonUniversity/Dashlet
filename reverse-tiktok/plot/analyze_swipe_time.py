import numpy as np


outcome = {2: [], 3: [], 4: [], 5: []}


for netid in range(2, 13):
    for swipeid in range(2, 6):

        foldername = f"../data/trace-{netid/2:.1f}-swipe-{swipeid}/"
        swipe_log_name = f"trace-{netid/2:.1f}-swipe-{swipeid}-swipe.log"

        # data = np.loadtxt(foldername + swipe_log_name)

        swipe_time = []
        fd = open(foldername + swipe_log_name)

        lines = fd.readlines()

        for line in lines:
            if len(line) > 5:
                items = line.split(",")

                swipe_time.append(float(items[1]))

        for i in range(1, len(swipe_time)):

            outcome[swipeid].append(swipe_time[i] - swipe_time[i-1])

        fd.close()

print(np.average(outcome[2]))
print(np.average(outcome[3]))
print(np.average(outcome[4]))
print(np.average(outcome[5]))
