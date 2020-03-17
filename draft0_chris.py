#!/bin/env python

# Setup
filepath = "./test0.txt"
K = 10

# Libraries
import numpy
jiulian = __import__("jiulian")

# Parse file
file = open(filepath)
lines = file.readlines()
file.close()
lines = [line[:-1].split(' ') for line in lines]

header = lines[0]
meta = lines[1]
data = numpy.array(lines[2:]).T

JDHEL = data[header.index("JDHEL")]
VC = data[header.index("V-C")]
HELCOR= data[header.index("HELCOR")]
dates = [jiulian.from_jd(float(mjd), fmt='jd') for mjd in JDHEL]

#print([date.strftime("%b %d %Y %H:%M:%S") for date in dates])


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
    vals = [getVal(i - j) for j in range(-nb_vals, +nb_vals)]
    errors[i] = sum(vals) / 



# Find local maxima



# Fit between SE maxima



# Deduce parameters


def getVal(i, arr) :
    if i <= 0:
        return arr[0]
    if i >= len(arr):
        return arr[-1]
    else:
        return arr[i]