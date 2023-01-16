import time
import pyautogui
from datetime import datetime

def record():

	for i in range(15):
		pos = pyautogui.position()

		print(pos)

		time.sleep(1)


if __name__ == '__main__':

	record()


