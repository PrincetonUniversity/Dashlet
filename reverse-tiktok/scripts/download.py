import csv
import json
import os
from pathlib import Path


IDX_URL = 5
IDX_URI = 1

fd = open("../config.json")
configurations = json.load(fd)
exp_name = configurations["exp_name"]


table_list = []


with open(f"../data/{exp_name}/{exp_name}-play.csv", newline='') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

	for row in spamreader:
		table_list.append(row)
	

for i in range(len(table_list)):
	if len(table_list[i]) == 1:
		continue
	if len(table_list[i][IDX_URL].strip()) > 15:

		videofile = f"../video/{table_list[i][IDX_URI]}.mp4"
		if Path(videofile).is_file() == False:
			cmd = f"curl -o {videofile} {table_list[i][IDX_URL].strip()}"

			os.system(cmd)