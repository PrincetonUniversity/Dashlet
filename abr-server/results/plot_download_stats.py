import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
import time
import os
import argparse
plt.rcParams.update({'font.size': 14})


from statsmodels.distributions.empirical_distribution import ECDF


dashlet_folder = "./"
tt_folder = "/home/acer/Documents/reverse-tiktok/plot/"

download_percentage_tt = np.loadtxt(tt_folder+"download-percentage-tt.txt")
effect_download_tt = np.loadtxt(tt_folder+"effect-download-tt.txt")


download_percentage_dashlet = np.loadtxt(dashlet_folder+"download-percentage-dashlet.txt")
effect_download_dashlet = np.loadtxt(dashlet_folder+"effect-download-dashlet.txt")


ecdf_tt = ECDF(download_percentage_tt)
ecdf_dashlet = ECDF(download_percentage_dashlet)
plt.plot(ecdf_tt.x, ecdf_tt.y, label="TikTok", lw=3)
plt.plot(ecdf_dashlet.x, ecdf_dashlet.y, label="Dashlet", lw=3)
plt.legend()
plt.grid()
# plt.show()
plt.ylabel("CDF")
plt.xlabel("Time to download / Total time")
plt.savefig("download-percentage.png", bbox_inches='tight')
plt.close()


ecdf_tt = ECDF(effect_download_tt)
ecdf_dashlet = ECDF(effect_download_dashlet)
plt.plot(ecdf_tt.x, ecdf_tt.y, label="TikTok", lw=3)
plt.plot(ecdf_dashlet.x, ecdf_dashlet.y, label="Dashlet", lw=3)
plt.legend()
plt.grid()
# plt.show()
plt.ylabel("CDF")
plt.xlabel("Viewed data / Downloaded data")
plt.savefig("effect-download.png", bbox_inches='tight')
plt.close()



