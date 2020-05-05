from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, 
    QTextEdit, QGridLayout, QApplication, QGroupBox, QVBoxLayout, QWidget, QSlider, QFileDialog, QDialog, QDialogButtonBox)
from PyQt5.QtGui import QDoubleValidator

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import linregress
from datetime import datetime
from matplotlib.widgets import Slider
from math import floor

from scipy.ndimage import gaussian_filter1d

jiulian = __import__("jiulian")

progname = os.path.basename(sys.argv[0])


def getVal(i, arr) :
    if i <= 0:
        return arr[0]
    if i >= len(arr):
        return arr[-1]
    else:
        return arr[i]

def smooth(inlist, param):
    return gaussian_filter1d(inlist, param)

def Find_tftt(T, kp, Y):
    mean = sum(Y)/len(Y)
    Up_1 = 0
    Down_1 = 0
    Up_2 = 0
    Down_2 = 0

    for i in range(len(Y)):
        if (Y[i] < mean and Down_1 == 0):
            Down_1 = T[kp[i]]
        elif (Y[i] < mean and Down_1 != 0):
            Down_2 = T[kp[i]]
        else:
            if (Down_1 == 0):
                Up_1 = T[kp[i]]
            elif(Down_2 != 0 and Up_2 == 0):
                Up_2 = T[kp[i]]
    
    T_t = Up_2 - Up_1
    if Down_2 == 0:
        T_f = 0
    else:
        T_f = Down_2 - Down_1
    return T_t, T_f


def Param(R_star, Period, time, k_ps, Y):
    """
    Input : Radius of the star, Period in seconds,
    timestamp in seconds, kept_peaks, magnitude
    """
    # Light curve data
    T_t, T_f = Find_tftt(time, k_ps, Y)
    Depth = abs(max(Y) - min(Y))
    print("\t",T_t)
    print("\t",T_f)
    # Impact parameter b
    sinT_t = np.float_power( np.sin(T_t * np.pi/Period), 2) 
    sinT_f = np.float_power( np.sin(T_f * np.pi/Period), 2)

    return Depth, sinT_t, sinT_f, T_t, T_f

def Impact_parameter(sinT_t, sinT_f, Depth):
    """
    Input : sin^2(T_t*pi/Period), sin^2(T_f*pi/Period),
    Depth
    """
    A = np.float_power((1 + np.sqrt(Depth)), 2)
    B = np.float_power((1 - np.sqrt(Depth)), 2)
    b = np.sqrt(abs(B - sinT_f*A/sinT_t) / (1 - sinT_f/sinT_t))
    return b

def Semimajor(R_star, sinT_t, Depth, b):
    """
    Input : Radius of the star, sin^2(T_t*pi/Period),
    Depth (or Delta Flux), impact parameter b
    """
    A = np.float_power((1 + np.sqrt(Depth)), 2)
    a = R_star * np.sqrt(abs(A - (1-sinT_t)*np.float_power(b, 2)) / (sinT_t))
    return a

def Inclinaison(R_star, a, b):
    """
    Input : Radius of the star, semi-major axis a,
    impact parameter b
    """
    i = np.arccos(R_star*b/a)
    return i*180/np.pi

def Planet_radius(R_star, Depth):
    Rp = R_star*np.sqrt(Depth)
    return Rp

def Star_density(Depth, b, sinT_t, Period):
    G = 6.67430 * np.float_power(10, -17)
    A = np.float_power((1 + np.sqrt(Depth)), 2)
    x1 = (4* np.float_power(np.pi, 2) )/(G* np.float_power(Period, 2))
    x2 = (A-np.float_power(b, 2)*(1-sinT_t)) / sinT_t

    rho_star = x1 * np.float_power(x2, 3/2)
    return rho_star

def Star_mass(R_star, rho_star):
    M_star = (4/3) * np.pi * rho_star * np.float_power(R_star, 3)
    return M_star

def Planet_mass(M_star, Period, a):
    G = 6.67430 * np.float_power(10, -17)
    M_planet = abs((4 * np.float_power(np.pi, 2) * np.float_power(a, 3))/(G * np.float_power(Period, 2)) - M_star)
    return M_planet

class CustomDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(CustomDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("About")
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.label = QLabel("Built by Chris de CLAVERIE and Magdalena Calka !\nIPSA CIRI Exoplanet Transits 2020")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig = fig
        self.axes = fig.add_subplot(111)
        super(Canvas, self).__init__(fig)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Open', self.OpenFile,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.help_menu.addAction('&About', self.About)
        self.menuBar().addMenu(self.help_menu)

        self.main_widget = QtWidgets.QWidget(self)

        
        self.setGeometry(50, 50, 800, 800)
        self.setWindowTitle('Review')    
        

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        grid = QGridLayout(self.main_widget)
        grid.addWidget(self.GroupGraph(), 0,0)
        grid.addWidget(self.GroupResult(),0,1)
        grid.setSpacing(10)

        self.k = 8
        self.a = 0
        self.b = 0

        self.Star_Radius = 1.0
        self.Period = 1.0
        
    def About(self):
        dlg = CustomDialog(self)
        dlg.exec_()

    def OpenFile(self):
        file = QFileDialog.getOpenFileName(self, 'Open File')
        if file[0]:
            aw.setWindowTitle("%s [%s]" % (progname, file[0]))
            # Parse file
            file = open(file[0], 'r')
            lines = file.readlines()
            file.close()
            self.lines = [line[:-1].split(' ') for line in lines]
            self.parseData()

    def parseData(self):
        if not hasattr(self, "lines"):
            return

        lines = self.lines
        header = lines[0]
        meta = lines[1]
        data = np.array([x for x in lines[2:] if x[header.index("V-C")] != "99.99999"]).T

        JDHEL = data[header.index("JDHEL")]
        VC = data[header.index("V-C")]
        VC = [-1 * float(d) for d in VC]
        #HELCOR= data[header.index("HELCOR")]
        dates = [jiulian.from_jd(float(mjd), fmt='jd') for mjd in JDHEL]
        timestamps_orig = [datetime.timestamp(i) for i in dates]
        timestamps = [i-timestamps_orig[0] for i in timestamps_orig]

        a = self.a 
        b = self.b
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
        nb_vals = int(self.k * resolution)
        VC = smooth(VC, self.s)

        #print([date.strftime("%b %d %Y %H:%M:%S") for date in dates])
        #print(VC)
        self.dataCanvas.axes.clear()
        self.dataCanvas.axes.set_title("Data")
        self.dataCanvas.axes.plot(timestamps, [float(d) for d in VC])

        # Compute standard errors (use tunable parameter)
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
        self.errorCanvas.axes.clear()
        self.errorCanvas.axes.set_title('Standard errors')
        self.errorCanvas.axes.plot(timestamps, errors_smoothed)

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
            self.errorCanvas.axes.axvline(x=timestamps[kept_peaks[i]], color='red')

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

        Depth, sintt, sintf, Tot, full = Param(R_s, Period, timestamps, boundaries, mag)
        imp_b = Impact_parameter(sintt, sintf, Depth)
        Semi_a = Semimajor(R_s, sintt, Depth, imp_b)
        alpha = Inclinaison(R_s, Semi_a, imp_b)
        R_p = Planet_radius(R_s, Depth)
        Star_d = Star_density(Depth, imp_b, sintt, Period)
        M_star = Star_mass(R_s, Star_d)
        M_planet = Planet_mass(M_star, Period, Semi_a)

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


    def GroupGraph(self):
         #graphics and toolbars        
        Rd = Canvas(self.main_widget, width=5, height=5, dpi=100)
        self.dataCanvas = Rd
        Cd = Canvas(self.main_widget, width=5, height=5, dpi=100)
        self.errorCanvas = Cd
        toolbarRd = NavigationToolbar(Rd, self)
        toolbarCd = NavigationToolbar(Cd, self)

        groupBoxGraph = QGroupBox('Graphics and toolbars')
        vbox = QVBoxLayout()
        vbox.addWidget(toolbarRd)
        vbox.addWidget(Rd)
        vbox.addWidget(toolbarCd)
        vbox.addWidget(Cd)
        vbox.addStretch(1)
        groupBoxGraph.setLayout(vbox)       
        
        return groupBoxGraph
        
    def GroupResult(self):
        labelRadius = QtWidgets.QLabel()
        labelRadius.setText("Enter the Star's radius (solar radius):")

        labelPeriod = QtWidgets.QLabel()
        labelPeriod.setText("Enter the Period of orbit (days):")

        self.PlanetLabel = QLabel('Planet radius : \nPlanet mass : ')
        self.StarLabel = QLabel('Star density : \nStar mass : ')
        self.Other = QLabel('Impact parameter b : \nSemimajor axis a : \nInclinaison : ')
        self.LC = QLabel('Depth : \nTotal duration : \nFull duration : ')

        self.labelInfosK = QLabel('Change the K coefficient :  (note: coeff was calculated to be optimal)')

        self.labelInfosS = QLabel('Change the s coefficient : ')

        labelInfosA = QtWidgets.QLabel()
        labelInfosA.setText('Change boundary values from left and right :')

        tuto1 = "The K coefficient characterize the time's interval used for error calculation.\nIncrease K implies less approximation segments."
        tuto2 = "\n\nThe s coefficient is the number of samples used to smooth the data."
        labeltuto = QLabel(tuto1+tuto2)

        self.validator = QDoubleValidator()
        self.RS_input = QLineEdit()
        self.RS_input.setValidator(self.validator)
        self.RS_input.returnPressed.connect(self.RadiusChanged)
        
        self.Per_input = QLineEdit()
        self.Per_input.setValidator(self.validator)
        self.Per_input.returnPressed.connect(self.PeriodChanged)

        sliderS = QSlider(Qt.Horizontal)
        sliderS.setFocusPolicy(Qt.StrongFocus)
        sliderS.setTickPosition(QSlider.TicksBothSides)
        sliderS.setTickInterval(10)
        sliderS.setSingleStep(1)
        sliderS.setMinimum(1)
        sliderS.valueChanged.connect(self.changeS)
        self.ss = sliderS
        sliderS.setValue(2)

        sliderK = QSlider(Qt.Horizontal)
        sliderK.setFocusPolicy(Qt.StrongFocus)
        sliderK.setTickPosition(QSlider.TicksBothSides)
        sliderK.setTickInterval(10)
        sliderK.setSingleStep(1)
        sliderK.setMinimum(2)
        sliderK.valueChanged.connect(self.changeK)
        self.sk = sliderK
        sliderK.setValue(8)

        sliderA = QSlider(Qt.Horizontal)
        sliderA.setFocusPolicy(Qt.StrongFocus)
        sliderA.setTickPosition(QSlider.TicksBothSides)
        sliderA.setTickInterval(10)
        sliderA.setSingleStep(1)
        sliderA.valueChanged.connect(self.changeA)
        self.sa = sliderA
        sliderA.setValue(0)

        sliderB = QSlider(Qt.Horizontal)
        sliderB.setFocusPolicy(Qt.StrongFocus)
        sliderB.setTickPosition(QSlider.TicksBothSides)
        sliderB.setTickInterval(10)
        sliderB.setSingleStep(1)
        sliderB.valueChanged.connect(self.changeB)
        sliderB.setInvertedAppearance(True)
        self.sb = sliderB
        sliderB.setValue(0)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(sliderA)
        hbox.addWidget(sliderB)

        GridResult = QGridLayout()
        #User Input
        GridResult.addWidget(labelRadius, 0,0)
        GridResult.addWidget(self.RS_input, 1,0)
        GridResult.addWidget(labelPeriod, 0,1)
        GridResult.addWidget(self.Per_input, 1,1)
        
        #Deduced Parameter
        GridResult.addWidget(self.PlanetLabel, 2,0)
        GridResult.addWidget(self.StarLabel, 3,0)
        GridResult.addWidget(self.LC, 2,1)
        GridResult.addWidget(self.Other, 3,1)

        groupBoxResult = QGroupBox('Results')
        vbox = QVBoxLayout()
        vbox.addLayout(GridResult)
        vbox.addWidget(self.labelInfosK)
        vbox.addWidget(sliderK)
        vbox.addWidget(self.labelInfosS)
        vbox.addWidget(sliderS)
        vbox.addWidget(labelInfosA)
        vbox.addLayout(hbox)
        vbox.addWidget(labeltuto)
        vbox.addStretch(1)
        groupBoxResult.setLayout(vbox)       
        
        return groupBoxResult


    def fileQuit(self):
        self.close()

    def RadiusChanged(self):
        self.Star_Radius = float(self.RS_input.text())
        self.compute_figures()

    def PeriodChanged(self):
        self.Period = float(self.Per_input.text())
        self.compute_figures()

    def changeS(self):
        self.s = self.ss.value()
        self.compute_figures()

    def changeA(self):
        self.a = self.sa.value()
        self.compute_figures()

    def changeB(self):
        self.b = self.sb.value()
        self.compute_figures()

    def changeK(self):
        self.k = self.sk.value()
        self.compute_figures()

    def compute_figures(self):
        self.parseData()

qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())

datax = [random.random() for i in range(25)]
datay = [random.random() for i in range(25)]