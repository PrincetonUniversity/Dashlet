import os
import numpy as np


IN_FILE = './cooked/'
OUT_FILE = './mahimahi/'
FILE_SIZE = 2000
BYTES_PER_PKT = 1500.0
MILLISEC_IN_SEC = 1000.0
EXP_LEN = 20000.0  # millisecond


def main():

	with open("trace.up", 'wb') as mf:
		millisec_time = 0
		mf.write(str(millisec_time) + '\n')
		for i in range(1000):
			throughput = 2000000 / 8
			pkt_per_millisec = throughput / BYTES_PER_PKT / MILLISEC_IN_SEC

			millisec_count = 0
			pkt_count = 0
			while True:
				millisec_count += 1
				millisec_time += 1
				to_send = (millisec_count * pkt_per_millisec) - pkt_count
				to_send = np.floor(to_send)

				for i in xrange(int(to_send)):
					mf.write(str(millisec_time) + '\n')

				pkt_count += to_send

				if millisec_count >= EXP_LEN:
						break


if __name__ == '__main__':
	main()
