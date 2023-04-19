import sys
import os
import subprocess
import numpy as np


RUN_SCRIPT = 'test.py'
RANDOM_SEED = 42
RUN_TIME = 320  # sec
MM_DELAY = 40   # millisec


def main():
	# trace_path = sys.argv[1]
	trace_path = "~/Documents/dashlet/reverse-tiktok/traces/network/trace-6.0.down"
	process_id = '0'

	sleep_vec = [i for i in range(1, 10)]  # random sleep second

	# files = os.listdir(trace_path)
	files = [trace_path]
	for f in files:

		while True:

			# np.random.shuffle(sleep_vec)
			# sleep_time = sleep_vec[int(process_id)]

			print('mm-delay ' + str(MM_DELAY) + 
					  ' mm-link 12mbps ' + trace_path + f + ' ' +
					  'python3 ' + RUN_SCRIPT)
			
			proc = subprocess.Popen('mm-delay ' + str(MM_DELAY) + 
					  ' mm-link 12mbps ' + trace_path + f + ' ' +
					  'python3 ' + RUN_SCRIPT,
					  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

			(out, err) = proc.communicate()


			break

			# if out == 'done\n':
			# 	break
			# else:
			# 	with open('./chrome_retry_log', 'ab') as log:
			# 		log.write(abr_algo + '_' + f + '\n')
			# 		log.write(out + '\n')
			# 		log.flush()



if __name__ == '__main__':
	main()
