import os
import random
import csv




foldername = "/home/acer/Downloads/mturk-code/createhit/gooddata/"
filenames = os.listdir(foldername)

result_dict = {}

for filename in filenames:
    with open(foldername+filename, newline='') as csvfile:
        print(filename)
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if row[2] == 'NaN':
                continue
            if row[0] == 'countdown':
                continue

            if row[0] not in result_dict.keys():
                result_dict[row[0]] = []

            result_dict[row[0]].append(float(row[1]))





files = os.listdir("../video-buffer/")

ofiles = []

for file in files:
    if file[0] == "v" and file[-1] == "4":
        fnamet = file.strip(".mp4")

        if fnamet not in result_dict.keys() or len(result_dict[fnamet]) < 25:
            ofiles.append(fnamet)

countdown_num = int(len(ofiles) / 33)

for i in range(countdown_num):
    ofiles.append("countdown")
random.seed(0)
random.shuffle(ofiles)


outstring = "var vids = [\"" + "\", \"".join(ofiles) + "\"];"

fd = open("data.js", "w")
fd.write(outstring)
fd.close()