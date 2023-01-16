import csv

import os
from pathlib import Path

listdir = []
IDX_URI = 1
IDX_URL = 5

for uid in range(101, 111):

    net_condition_list = ["low", "mid", "high"]

    for nc in net_condition_list:

        exp_name = f"tt-{uid}-{nc}"

        table_list = []

        with open(f"../data/{exp_name}/{exp_name}-play.csv", newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

            for row in spamreader:
                table_list.append(row)

        for i in range(len(table_list)):

            if len(table_list[i]) < IDX_URL:
                continue

            if len(table_list[i][IDX_URL].strip()) > 15:

                videofile = f"../video/{table_list[i][IDX_URI]}.mp4"
                outfiles = f"../video-buffer/{table_list[i][IDX_URI]}.mp4"
                if Path(videofile).is_file() == False:
                    print(videofile)
                    print(exp_name)
                else:
                    os.system(f"cp {videofile} {outfiles}")

