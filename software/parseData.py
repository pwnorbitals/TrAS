from datetime import datetime
import numpy as np
import computations as comp
import jiulian as jd


# Numpy, scipy, datetime
from scipy.signal import find_peaks
from scipy.stats import linregress
from scipy.ndimage import gaussian_filter1d

    # Extract part of an array around a position with a given size : arr[pos-halfsize, pos+halfsize]
def windowAround(arr, pos, halfsize):
    start = 0
    if pos - halfsize < 0:
        start = 0
    else:
        start = pos - halfsize

    end = len(arr)
    if pos + halfsize > len(arr):
        end = len(arr)
    else:
        end = pos + halfsize

    return arr[start:end]

    # Smooth an array with a given smoothing parameter (lower = less smoothing)
def smooth(inlist, param):
    return gaussian_filter1d(inlist, param)

def parseData(self):
        if not hasattr(self, "lines"):
            return

        lines = self.lines
        header = lines[0]

        self.ListRefStar = comp.Header(header)
        self.ChoiceOfStar()
        
        meta = lines[1]
        data = np.array([x for x in lines[2:] if x[header.index(self.Y)] != "99.99999"]).T

        JDHEL = data[header.index("JDHEL")]
        VC = data[header.index(self.Y)]
        VC = [-1 * float(d) for d in VC]
        #HELCOR= data[header.index("HELCOR")]
        dates = [jd.from_jd(float(mjd), fmt='jd') for mjd in JDHEL]
        timestamps_orig = [datetime.timestamp(i) for i in dates]
        timestamps = [i-timestamps_orig[0] for i in timestamps_orig]

        a = self.sa.value()
        b = self.sb.value()
        JDHEL = JDHEL[a : -(b+1)]
        VC = VC[a : -(b+1)]
        timestamps = timestamps[a : -(b+1)]
        dates = dates[a : -(b+1)]       


        # Compute resolution 
        timediff = max(dates) - min(dates)
        timediff_min = timediff.total_seconds() / 60
        print("Time difference : ", timediff, "(", timediff_min, " minutes)")

        resolution = timediff_min / len(VC)
        print("Resolution : ", resolution, " samples per minute")


        # Compute tunable time parameter
        nb_vals = int(self.sk.value() * resolution)
        VC = smooth(VC, self.ss.value())

        #print([date.strftime("%b %d %Y %H:%M:%S") for date in dates])
        #print(VC)
        self.dataCanvas.axes.clear()
        self.dataCanvas.axes.set_title("Data")
        self.dataCanvas.axes.plot(timestamps, [float(d) for d in VC], linewidth=1.0)

        # Compute standard errors (use tunable parameter)
        errors = []
        for i in range(len(VC)):
            #vals = [float(getVal(i + j, VC)) for j in range(-nb_vals, +nb_vals)]
            vals = windowAround(VC, i, nb_vals)
            errors.append(np.std(vals))

            #print(errors)
        errors_smoothed = smooth(errors, nb_vals)
        self.errorCanvas.axes.clear()
        self.errorCanvas.axes.set_title('Standard errors')
        self.errorCanvas.axes.plot(timestamps, errors_smoothed, linewidth=1.0)

        # Find local maxima
        peaks, properties = find_peaks(errors_smoothed, prominence=10**(-self.sp.value()))
        print("PEAKS : ", peaks)
        print("PEAKS Y : ", errors_smoothed[peaks])

        prominences = properties["prominences"]
        #print("PROMINENCES : ", prominences)

        sort_arr = [[i, peaks[i], prominences[i]] for i in range(len(peaks))]

        sorted_kept_peaks = sorted(sort_arr, key=lambda entry: entry[2], reverse=True)[:6]
        kept_peaks = [elem[1] for elem in sorted_kept_peaks]

        for i in range(len(kept_peaks)):
            self.errorCanvas.axes.axvline(x=timestamps[kept_peaks[i]], color='blue')

        # Fit between SE maxima (linear regression)
        # https://exoplanetarchive.ipac.caltech.edu/docs/datasethelp/AXA.html
        # http://brucegary.net/AXA/Fitting/fitting.html
        fits = []
        kept_peaks.insert(0, 0)
        kept_peaks = sorted(kept_peaks)
        print("KEPT PEAKS : ", kept_peaks)
        
        # Add list mag to get the begin of each approximation
        boundaries = []
        mag = []
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
            #self.dataCanvas.axes.plot(y, xvals)
            self.dataCanvas.axes.plot(xvals, yvals)
            #print(fits)
            mag.extend([yvals[0], yvals[-1]])
            boundaries.extend([min_of_range, max_of_range-1])

        self.errorCanvas.fig.canvas.draw()
        self.errorCanvas.fig.canvas.flush_events()
        self.dataCanvas.fig.canvas.draw()
        self.dataCanvas.fig.canvas.flush_events()


            # Deduce parameters
        
        #Conversion in km and in seconds
        Sun_rad = 695700
        R_s = self.Star_Radius * Sun_rad
        Period = self.Period * 86400

        Depth, sintt, sintf, Tot, full = comp.Param(R_s, Period, timestamps, boundaries, mag)
        imp_b = comp.Impact_parameter(sintt, sintf, Depth)
        Semi_a = comp.Semimajor(R_s, sintt, Depth, imp_b)
        alpha = comp.Inclinaison(R_s, Semi_a, imp_b)
        R_p = comp.Planet_radius(R_s, Depth)
        Star_d = comp.Star_density(Depth, imp_b, sintt, Period)
        M_star = comp.Star_mass(R_s, Star_d)
        M_planet = comp.Planet_mass(M_star, Period, Semi_a)

        planet = "Planet radius : %.5E (km)" % R_p + "\nPlanet mass : %.3E (kg)" % M_planet
        star = "Star density : %.5E" % Star_d + "\nStar mass : %.3E (kg)" % M_star
        other = "Impact parameter b : %.5E" % imp_b + "\nSemi-major a : %.5E (km)" % Semi_a + "\nInclinaison : %.3f °" % alpha
        lightcurve = "Depth : %.3f" % Depth + "\nTotal duration : %.3E" % Tot + "\nFull duration : %.3E" % full

        self.PlanetLabel.setText(planet)
        self.StarLabel.setText(star)
        self.Other.setText(other)
        self.LC.setText(lightcurve)

        self.labelInfosK.setText('Change the K coefficient : %i  (note: coeff was calculated to be optimal)' % self.sk.value())
        self.labelInfosS.setText('Change the s coefficient : %i' % self.ss.value())