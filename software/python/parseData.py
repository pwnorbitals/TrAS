from datetime import datetime
import numpy as np
import computations as comp
import jiulian as jd
import LightCurvePlot as LCP


# Numpy, scipy, datetime
from scipy.signal import find_peaks
from scipy.stats import linregress
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d

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

def Linear(x, a, b):
    return a*x+b

def parseData(self):
        if not hasattr(self, "lines"):
            return

        lines = self.lines
        header = lines[0]

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
        VC = [float(d) for d in VC[a : -(b+1)]]
        timestamps = timestamps[a : -(b+1)]
        dates = dates[a : -(b+1)]       

        #timestamps_interp = list(np.arange(timestamps[0], timestamps[-1], 0.1))
        #VC_interp_fct = interp1d(timestamps, VC)
        #VC_interp = [VC_interp_fct(x) for x in timestamps_interp]


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
        self.dataCanvas.axes.plot(timestamps, VC, linewidth=1.0)
        #self.dataCanvas.axes.plot(timestamps_interp, VC_interp, linewidth=1.0)

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
        b = VC[0]
        tol = 1e-6
        for i in range(len(kept_peaks)):

            # subdivide interval
            min_of_range = kept_peaks[i]

            if i+1 == len(kept_peaks):
                max_of_range = len(timestamps)
            else:
                max_of_range = kept_peaks[i+1]
            #print(min_of_range, max_of_range)
            
            # get x and y data for linear regression on the interval | reduce time series to have x[0] = 0
            x = [i-timestamps[min_of_range] for i in timestamps[min_of_range:max_of_range]]
            y = VC[min_of_range:max_of_range]
            
            # run linear regression
            #fits.append(linregress(x,y)) # slope, intercept, r_value, p_value, std_err
            fits, cov = curve_fit(Linear, x, y, bounds=([-np.inf, b-tol],[np.inf,b]))
            
            # get x and y value after regression
            xvals = np.array(timestamps[min_of_range:max_of_range])
            b_star = b-fits[0]*xvals[0]
            #yvals = [fits[-1].slope * timestamps[j] + b for j in range(min_of_range, max_of_range)]
            yvals = Linear(xvals, fits[0], b_star)
            #self.dataCanvas.axes.plot(y, xvals)
            self.dataCanvas.axes.plot(xvals, yvals)
            #print(fits)
            mag.extend([yvals[0], yvals[-1]])
            boundaries.extend([min_of_range, max_of_range-1])
            b = yvals[-1]
            
            

        self.errorCanvas.fig.canvas.draw()
        self.errorCanvas.fig.canvas.flush_events()
        self.dataCanvas.fig.canvas.draw()
        self.dataCanvas.fig.canvas.flush_events()


            # Deduce parameters
        
        #Conversion parameters for output
        l = self.conversion[0]
        m = self.conversion[1]
        t = self.conversion[2]
        a = self.conversion[3]

        # Convert input to km and second
        R_s = self.Star_Radius / l
        Period = self.Period / t

        Depth, sintt, sintf, Tot, full, midtime = comp.Param(R_s, Period, timestamps, boundaries, mag)
        imp_b = comp.Impact_parameter(sintt, sintf, Depth)
        Semi_a = comp.Semimajor(R_s, sintt, Depth, imp_b)
        alpha = comp.Inclinaison(R_s, Semi_a, imp_b)
        R_p = comp.Planet_radius(R_s, Depth)
        Star_d = comp.Star_density(Depth, imp_b, sintt, Period)
        M_star = comp.Star_mass(R_s, Star_d)
        M_planet = comp.Planet_mass(M_star, Period, Semi_a)

        # Update Label
        #planet = "Planet radius : {0:.5E} {1} \nPlanet mass : {2:.3E} {3}".format((R_p*l), self.str_conv[0], (M_planet*m), self.str_conv[1])
        star = "Star density : {0:.5E} kg/m3 \nStar mass : {1:.3E} {2}".format(Star_d, (M_star*m), self.str_conv[1])
        other = "Impact parameter b : {0:.5E} \nSemi-major a : {1:.5E} {2} \nInclinaison : {3:.3f} {4}".format(imp_b, (Semi_a*l), self.str_conv[0], (alpha*a), self.str_conv[3])
        lightcurve = "Depth : {0:.3f} \nTotal duration : {1:.3E} {2} \nFull Duration : {3:.3E} {4}".format(Depth, (Tot*t), self.str_conv[2], (full*t), self.str_conv[2])

        self.labelRadius.setText("Enter the Star's radius (%s):"% self.str_conv[0])
        self.labelPeriod.setText("Enter the Period of orbit (%s):"% self.str_conv[2])

        self.PRadiusValue.setText(str(R_p*l))
        self.PMassValue.setText(str(M_planet*m))

        self.StarLabel.setText(star)
        self.Other.setText(other)
        self.LC.setText(lightcurve)

        self.labelInfosK.setText('Change the K coefficient : %i  (note: coeff was calculated to be optimal)' % self.sk.value())
        self.labelInfosS.setText('Change the s coefficient : %i' % self.ss.value())

        # LIGHT CURVE PLOTTING  
        flux = LCP.Theoretical_LC(Depth, R_s, timestamps, midtime, Period, Semi_a, imp_b)
        Norm = 1-comp.NormalizedMag(mag)

        self.theoricCanvas.axes.clear()
        self.theoricCanvas.axes.set_title('Analytical Light Curve')
        self.theoricCanvas.axes.plot(timestamps, flux, linewidth=1.0)
        self.theoricCanvas.axes.plot(timestamps, [d+Norm for d in VC], linewidth=1.0)

        self.theoricCanvas.fig.canvas.draw()
        self.theoricCanvas.fig.canvas.flush_events()