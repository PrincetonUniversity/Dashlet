import time
import pyautogui
import numpy as np
from datetime import datetime
import json
import argparse


class SwipeEngine:

	def __init__(self, iterations, swipetrace):
		self.startx = 2353
		self.starty = 800
		self.endx = 2353
		self.endy = 245

		self.seqidx = 0
		self.swipe_trace = ""
		self.swipe_name = swipetrace

		self.IDX_DURATION = 2

		self.swipe_records = np.loadtxt(self.swipe_name)

		self.iterations = iterations

		pyautogui.moveTo(self.startx, self.starty)
		pyautogui.dragTo(self.startx, self.starty-10, 0.2, button='left')

	def get_next_swipe_time(self):

		return 10


	def run(self):

		pyautogui.moveTo(self.startx, self.starty)
		time.sleep(0.1)
		pyautogui.dragTo(self.endx, self.starty-100, 0.2, button='left')

		time.sleep(60)

		for i in range(self.iterations):

			stime = time.time()

			self.swipe()

			next_swipe_time = -1
			
			for retries in range(3):
				next_swipe_time = self.get_next_swipe_time()
				if next_swipe_time < 0:
					time.sleep(2)
				else:
					break

			print(next_swipe_time)

			ctime = time.time()

			sleep_time = next_swipe_time - (ctime - stime) - 0.3

			if sleep_time > 0:
				time.sleep(sleep_time)





	def swipe(self):
		pyautogui.moveTo(self.startx, self.starty)
		time.sleep(0.1)
		pyautogui.dragTo(self.endx, self.endy, 0.2, button='left')

		self.seqidx += 1


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--swipetrace', default="../traces/swipe/swipe-2.txt", help='The network trace')

	args = parser.parse_args()

	se = SwipeEngine(80, args.swipetrace)

	se.run()
