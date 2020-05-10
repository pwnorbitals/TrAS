#!/bin/env python

# Setup
filepath = "./wasp43b_lekic.txt"
K = 8
max_peaks = 6
start_at = 20 #percents from the left
end_at_time = 10 #percents from the right

# Libraries
jiulian = __import__("jiulian")
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import linregress
from datetime import datetime
from matplotlib.widgets import Slider
from math import floor

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
VC = [-1 * float(d) for d in VC]
#HELCOR= data[header.index("HELCOR")]
dates = [jiulian.from_jd(float(mjd), fmt='jd') for mjd in JDHEL]
timestamps = [datetime.timestamp(i) for i in dates]

#print([date.strftime("%b %d %Y %H:%M:%S") for date in dates])
#print(VC)
#plt.plot(timestamps, [float(d) for d in VC])


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
    #print(vals)
    avg = np.average(vals)
    sn = np.sqrt((1/(len(vals)-1)) * sum([(xi - avg)**2 for xi in vals]) )  # Standard deviation
    #print(med, sn)
    errors.append(sn / np.sqrt(len(vals)))

#print(errors)
errors_smoothed = smooth(errors, nb_vals)
plt.plot(timestamps, errors_smoothed)


# Find local maxima
peaks, properties = find_peaks(errors_smoothed, prominence=1e-8)
print("PEAKS : ", peaks)
print("PEAKS Y : ", errors_smoothed[peaks])

prominences = properties["prominences"]
#print("PROMINENCES : ", prominences)

sort_arr = [[i, peaks[i], prominences[i]] for i in range(len(peaks))]

sorted_kept_peaks = sorted(sort_arr, key=lambda entry: entry[2], reverse=True)[:6]
kept_peaks = [elem[1] for elem in sorted_kept_peaks]

for i in range(len(kept_peaks)):
    plt.axvline(x=timestamps[kept_peaks[i]], color='red')

# Fit between SE maxima (linear regression)
# https://exoplanetarchive.ipac.caltech.edu/docs/datasethelp/AXA.html
# http://brucegary.net/AXA/Fitting/fitting.html
fits = []
kept_peaks.insert(0, 0)
kept_peaks = sorted(kept_peaks)
print("KEPT PEAKS : ", kept_peaks)
for i in range(len(kept_peaks)):

    # subdivide interval
    min_of_range = kept_peaks[i]

    if i+1 == len(kept_peaks):
        max_of_range = len(timestamps)
    else:
        max_of_range = kept_peaks[i+1]
    #print(min_of_range, max_of_range)

    # get x and y data for linear regression on the interval
    x = timestamps[min_of_range:max_of_range]
    y = VC[min_of_range:max_of_range]

    # run linear regression
    fits.append(linregress(x,y)) # slope, intercept, r_value, p_value, std_err

    # get x and y value after regression
    xvals = timestamps[min_of_range:max_of_range]
    yvals = [fits[-1].slope * timestamps[j] + fits[-1].intercept for j in range(min_of_range, max_of_range)]
    #plt.plot(y, xvals)
    #plt.plot(xvals, yvals)
#print(fits)



# Deduce parameters


plt.show()