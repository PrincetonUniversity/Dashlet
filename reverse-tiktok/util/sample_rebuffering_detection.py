import pyautogui
import numpy as np

import matplotlib.pyplot as plt



from PIL import Image
  
# Read image
# myScreenshot = Image.open("../tmp/s4.png")



def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

myScreenshot = pyautogui.screenshot(region=(3305, 935, 500, 6))



print(myScreenshot)


kk = np.array(myScreenshot.getdata())

pix = np.array(myScreenshot.getdata()).reshape(myScreenshot.size[1], myScreenshot.size[0], 3)



background = np.mean(pix[[0, 1, 4, 5], :,:], axis=0)

foreground = pix[2, :, :]

diff = np.abs(foreground - background)


print(np.shape(diff))

data = np.mean(diff, axis=1)

print(np.mean(diff))

plt.plot(data)
plt.show()

# print(np.shape(pix[:, [0, 1, 4, 5],:]))


# p1 = np.mean(pix, axis=2)


# # p1 = pix[:,:,2]

# print(np.mean(p1, axis=0))

# # print(np.mean(pix, axis=2))
myScreenshot.save("../tmp/s1.png")


# data = p1[:,2] - (p1[:,1] + p1[:,0] + p1[:,4] + p1[:,5]) / 4


# print(np.mean(data))
# # print(data)


# data = moving_average(data, n=30)

# plt.plot(data)
# plt.show()

print(foreground)