import pyautogui
import numpy as np

import matplotlib.pyplot as plt

import time
import json


cdf = open("../config.json")
configurations = json.load(cdf)
cdf.close()

exp_name = configurations["exp_name"]

fd = open(f"../data/{exp_name}/{exp_name}-rebuffering.log", "w")

def getval():
	myScreenshot = pyautogui.screenshot(region=(3305, 935, 500, 6))

	pix = np.array(myScreenshot.getdata()).reshape(myScreenshot.size[1], myScreenshot.size[0], 3)

	background = np.mean(pix[[0, 1, 4, 5], :,:], axis=0)

	foreground = pix[2, :, :]

	diff = np.abs(foreground - background)

	fd.write(f"{float(time.time()):.8f}, {np.mean(diff[125:375]):.2f}, {np.mean(diff[:20]):.2f}\n")

	print(np.mean(diff[125:375]), np.mean(diff[:20]))



while True:
	getval()

	time.sleep(0.1)
