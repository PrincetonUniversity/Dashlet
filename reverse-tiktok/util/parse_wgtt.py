import csv

import matplotlib.pyplot as plt

infolder = "../traces/wgtt/"
outfolder = "../traces/network/"

innames = ['tcp_10.csv', 'tcp_10_1.csv', 'tcp_20.csv']
outnames = ['wifi-10.down', 'wifi-11.down', 'wifi-12.down']

source_arr= ['dynamic-oit-vapornet100-10-9-169-230.princeton.edu', 'CableMat_60:7d', 'zhenyu-ThinkPad-T430.local']

for test_idx in range(3):
    result = {}

    ofd = open(outfolder+outnames[test_idx], "w")
    with open(infolder + innames[test_idx], newline='') as csvfile:

        reader = csv.DictReader(csvfile)

        start_time = -1
        buffered_bytes = 0

        for row in reader:


            if row['Source'] in source_arr and row['Protocol'] == '0x0803':



                if row['Destination'] == 'CableMat_60:01':

                    if start_time == -1:
                        start_time = float(row['Time'])

                    buffered_bytes += int(row['Length'])

                    if buffered_bytes > 1500:
                        message = int((float(row['Time']) - start_time) * 1000)

                        buffered_bytes -= 1500

                        ofd.write(str(message))
                        ofd.write("\n")

    ofd.close()


