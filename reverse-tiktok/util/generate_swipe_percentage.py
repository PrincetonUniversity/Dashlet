import numpy as np
import os
import scipy
from scipy.stats import expon
import random

print(scipy.__version__)

folderpath = "/home/acer/Documents/ttstream/testing/dataclean/data/"

filenanmes = os.listdir(folderpath)

swipe_data = np.zeros((0, 3))

for fname in filenanmes:

	full_path = f"{folderpath}{fname}"

	data = np.loadtxt(full_path)

	X = []

	# print(data)

	endcnt = 0
	noendcnt = 0

	for entry in data:
		percent = entry[1] / entry[0]

		# print(percent)

		if percent > 0.99999:
			endcnt += 1
		else:
			noendcnt += 1
			X.append(percent)

	print(endcnt)
	print(noendcnt)

	P = expon.fit(X, floc=0)

	print(P)


print(1-np.exp(-1 * 2))
print(1-np.exp(-1 * 3))
print(1-np.exp(-1 * 4))
print(1-np.exp(-1 * 5))



def sampling(lamba, num):
	nlen = int(num * 0.1)

	ret = []

	for i in range(nlen):
		ret.append(1.0)


	rlen = num - nlen


	prob = [(i+0.5) * 1.0 / rlen for i in range(rlen)]


	for i in range(rlen):
		val = -1 * np.log(1-prob[i]) / lamba

		if val > 1.0:
			val = 1.0


		ret.append(val)

	# print(ret)
	return ret


samplelength = 100

idx = [i for i in range(samplelength)]


random.seed(0)
random.shuffle(idx)

print(idx)


for lamba in range(2, 7):

	samples = sampling(lamba, samplelength)

	samples_shuffled = []
	
	for i in idx:
		samples_shuffled.append(samples[i])

	print(samples_shuffled)


	fd = open(f"../traces/swipe-{lamba}.txt", "w")

	for samle in samples_shuffled:

		fd.write(str(samle))
		fd.write("\n")

	fd.close()