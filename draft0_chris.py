#!/bin/env python

# Setup
filepath = "./test0.txt"
K = 20

# Libraries
jiulian = __import__("jiulian")
import numpy as np
import matplotlib.pyplot as plt

# Functions
def getVal(i, arr) :
    if i <= 0:
        return arr[0]
    if i >= len(arr):
        return arr[-1]
    else:
        return arr[i]


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

# Parse file
file = open(filepath)
lines = file.readlines()
file.close()
lines = [line[:-1].split(' ') for line in lines]

header = lines[0]
meta = lines[1]
data = np.array([x for x in lines[2:] if x[header.index("V-C")] != "99.99999"]).T

JDHEL = data[header.index("JDHEL")]
VC = data[header.index("V-C")]
HELCOR= data[header.index("HELCOR")]
dates = [jiulian.from_jd(float(mjd), fmt='jd') for mjd in JDHEL]

#print([date.strftime("%b %d %Y %H:%M:%S") for date in dates])
#print(VC)
#plt.plot([float(d) for d in VC])
#plt.show()


# Compute resolution 
timediff = max(dates) - min(dates)
timediff_min = timediff.total_seconds() / 60
print("Time difference : ", timediff, "(", timediff_min, " minutes)")

resolution = timediff_min / len(VC)
print("Resolution : ", resolution, " samples per minute")


# Compute standard errors (use tunable parameter)
nb_vals = int(K * resolution)
errors = []
for i in range(len(VC)):
    #min_max = (i - nb_vals, i + nb_vals)
    vals = [float(getVal(i + j, VC)) for j in range(-nb_vals, +nb_vals)]
    print(vals)
    med = np.average(vals)
    sn = np.sqrt((1/(len(vals)-1)) * sum([(xi - med)**2 for xi in vals]) )  # standard deviations with median
    print(med, sn)
    errors.append(sn / np.sqrt(len(vals)))

print(errors)
plt.plot(dates, smooth(errors, nb_vals))
plt.show()
# Find local maxima



# Fit between SE maxima



# Deduce parameters


