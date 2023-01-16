# import json
# import time
#
# cdf = open("../config.json")
# configurations = json.load(cdf)
# cdf.close()
#
# exp_name = configurations["exp_name"]
#
# fd = open(f"../data/{exp_name}/{exp_name}-start-time.log", "w")
#
#
# fd.write(str(time.time()))
# fd.close()

import numpy as np

def getcancellation(degree):

    val = (1 + np.cos(np.pi * (180 + degree) / 180)) / (1 + np.cos(np.pi * (0 + degree) / 180))

    print(val)

    db_val = 20 * np.log10(val)

    return db_val


print(getcancellation(10))