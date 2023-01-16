import time
import os
import numpy as np
import matplotlib.pyplot as plt
# folder = "/home/acer/Documents/ttstream/testing/networktrace/fcc/"


# files = os.listdir(folder)



# fd = open("throughput.txt", "w")

# for file in files:
# 	data = np.loadtxt(folder + file)


# 	bps = len(data) * 1500 * 8 / data[-1] / 1000

# 	print(bps)

# 	fd.write(f"{bps} - {file}\n")
# 	fd.flush()

# fd.close()




# import csv



# delta = [10 for i in range(20)]

# urls = ["" for i in range(20)]




# table_list = []

# highest = 0
# highest_url = ""

# with open(f"./throughput.csv", newline='') as csvfile:
# 	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

# 	for row in spamreader:
# 		table_list.append(row)


# 		# print(row)

# 		val = float(row[0])

# 		if val > highest:
# 			highest = val
# 			highest_url = row[1]


# 		for i in range(9, 20):

# 			diff = abs(val - i/2.0)


# 			if diff < delta[i]:
# 				delta[i] = diff

# 				urls[i] = row[1]


# print(delta)
# print(urls)

# for i in range(9, 20):
# 	tp = i/2
# 	cmd = f"mv ../traces/{urls[i].strip()} ../traces/{tp:.1f}.down"

# 	print(cmd)

# 	os.system(cmd)
# print(highest)
# print(highest_url)






for i in range(6, 20):
	tp = i/2
	fname = f"../traces/network/trace-{tp:.1f}.down"
	# fname = f"../traces/network.up"
	data = np.loadtxt(fname)

	nlen = int(data[-1] / 1000.0) + 1



	throughput = [0] * nlen


	for v in data:

		idx = int(v/1000.0)

		throughput[idx] += 1


	for j in range(nlen):
		throughput[j] = throughput[j] * 1500 * 8 / 1000 / 1000


	plt.plot(throughput)
	plt.show()


	print(np.mean(throughput))



# for i in range(9, 20):
# 	tp = i/2
# 	fname = f"../traces/{tp:.1f}.down"
# 	# fname = f"../traces/network.up"
# 	data = np.loadtxt(fname)

# 	oname = f"../traces/trace-{tp:.1f}.down"

# 	fd = open(oname, "w")

# 	for j in range(len(data)):

# 		if j % 2 == 0:
			
# 			fd.write(str(int(data[j] / 2)))
# 			fd.write("\n")


# 	fd.close()

# 	print(i)

	# nlen = int(data[-1] / 1000.0) + 1



	# throughput = [0] * nlen


	# for v in data:

	# 	idx = int(v/1000.0)

	# 	throughput[idx] += 1


	# for j in range(nlen):
	# 	throughput[j] = throughput[j] * 1500 * 8 / 1000 / 1000


	# plt.plot(throughput)
	# plt.show()


# def new():
# 	fname = f"../traces/network/trace-6.0.down"
# 	# fname = f"../traces/network.up"
# 	data = np.loadtxt(fname)

# 	oname = f"../traces/network/trace-3.0.down"

# 	fd = open(oname, "w")

# 	for j in range(len(data)):

# 		if j % 2 == 0:
			
# 			fd.write(str(int(data[j])))
# 			fd.write("\n")


# 	fd.close()

# new()