import time
import pyautogui
import numpy as np
from datetime import datetime
import json
import argparse


class SwipeEngine:

	def __init__(self, iterations, swipetrace):

		fd = open("../config.json")
		configurations = json.load(fd)
		exp_name = configurations["exp_name"]


		self.trace = ""

		self.startx = 3565
		self.starty = 671
		self.endx = 3565
		self.endy = 245

		self.seqidx = 0
		self.swipe_trace = ""
		self.video_durations = []
		self.log_name = f"../data/{exp_name}/{exp_name}-play.csv"
		self.swipe_name = swipetrace

		self.IDX_DURATION = 2

		self.outfile = open(f"../data/{exp_name}/{exp_name}-swipe.log", "w")
		self.swipe_records = np.loadtxt(self.swipe_name)

		self.iterations = iterations

		pyautogui.moveTo(self.startx, self.starty)
		pyautogui.dragTo(self.startx, self.starty-10, 0.2, button='left')


	def update_video_duration_from_log(self):

		self.video_durations = []

		with open(self.log_name) as fd:
			lines = fd.readlines()
			lines = [line.rstrip() for line in lines]


			nlen = len(lines)

			for i in range(nlen - 1):
				entries = lines[i].split(",")

				self.video_durations.append(int(entries[self.IDX_DURATION]) / 1000.0)


	def get_next_swipe_time(self):

		percentage = self.swipe_records[self.seqidx]

		if (self.seqidx >= len(self.video_durations)):
			self.update_video_duration_from_log()



		if (self.seqidx >= len(self.video_durations)):
			return -1

		return percentage * self.video_durations[self.seqidx]


	def run(self):

		for i in range(self.iterations):

			stime = time.time()

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

			self.swipe()



	def swipe(self):
		pyautogui.moveTo(self.startx, self.starty)
		time.sleep(0.1)
		pyautogui.dragTo(self.endx, self.endy, 0.2, button='left')
		now = datetime.now()
		my_time = now.strftime('%Y-%m-%d %H:%M:%S')
		self.outfile.write(str(my_time))
		self.outfile.write(", ")
		self.outfile.write(str(time.time()))
		self.outfile.write("\n")

		self.seqidx += 1


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--swipetrace', default="../traces/swipe/swipe-2.txt", help='The network trace')

	args = parser.parse_args()

	se = SwipeEngine(80, args.swipetrace)

	se.run()
