from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, 
    QTextEdit, QGridLayout, QApplication, QGroupBox, QVBoxLayout, QWidget, QSlider, QFileDialog)

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

jiulian = __import__("jiulian")

progname = os.path.basename(sys.argv[0])


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



class data(object):
	def __init__(self):
		self.dataX = dataX
		self.dataY = dataY
		self.processDataX = processDataX
		self.processDataY = processDataY
		self.repertory = repertory



class Canvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

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



"""

class DataCanvas(Canvas,data):    
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.cla()
        self.axes.plot(t, s)
        self.axes.set_title('Data')
    
    def compute_figure(self, a):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t*a)
        self.axes.clear()
        self.axes.plot(t, s)
        self.axes.set_title('Data')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

class ErrorsCanvas(Canvas,data):
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)
        self.axes.set_title('Standard errors')

    def compute_figure(self, k):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t*k)
        self.axes.clear()
        self.axes.plot(t, s)
        self.axes.set_title('Standard errors')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
"""

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.file_menu.addAction('&Open', self.OpenFile,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_N)
        self.menuBar().addMenu(self.file_menu)


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
        

    def OpenFile(self):
        file = QFileDialog.getOpenFileName(self, 'Open File')
        if file[0]:
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
        timestamps = [datetime.timestamp(i) for i in dates]

        a = self.a 
        b = self.b
        JDHEL = JDHEL[a : -(b+1)]
        VC = VC[a : -(b+1)]
        timestamps = timestamps[a : -(b+1)]
        dates = dates[a : -(b+1)]

        #print([date.strftime("%b %d %Y %H:%M:%S") for date in dates])
        #print(VC)
        self.dataCanvas.axes.clear()
        self.dataCanvas.axes.set_title("Data")
        self.dataCanvas.axes.plot(timestamps, [float(d) for d in VC])
        


        # Compute resolution 
        timediff = max(dates) - min(dates)
        timediff_min = timediff.total_seconds() / 60
        print("Time difference : ", timediff, "(", timediff_min, " minutes)")

        resolution = timediff_min / len(VC)
        print("Resolution : ", resolution, " samples per minute")


        # Compute standard errors (use tunable parameter)
        nb_vals = int(self.k * resolution)
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

        self.errorCanvas.fig.canvas.draw()
        self.errorCanvas.fig.canvas.flush_events()
        self.dataCanvas.fig.canvas.draw()
        self.dataCanvas.fig.canvas.flush_events()


            # Deduce parameters


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
        labelResult = QtWidgets.QLabel()
        labelResult.setText('Some random text, it\'s here we \n gonna show our results \n \n')

        labelInfosK = QtWidgets.QLabel()
        labelInfosK.setText('change k coeff slider \n(note: coeff was calculated to be optimal)')

        labelInfosA = QtWidgets.QLabel()
        labelInfosA.setText('change number of points for moving average \n(note: number of points was calculated to be optimal)')


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
        self.sb = sliderB
        sliderB.setValue(0)

        groupBoxResult = QGroupBox('Results')
        vbox = QVBoxLayout()
        vbox.addWidget(labelResult)
        vbox.addWidget(labelInfosK)
        vbox.addWidget(sliderK)
        vbox.addWidget(labelInfosA)
        vbox.addWidget(sliderA)
        vbox.addWidget(sliderB)
        vbox.addStretch(1)
        groupBoxResult.setLayout(vbox)       
        
        return groupBoxResult


    def fileQuit(self):
        self.close()


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



datax = [random.random() for i in range(25)]
datay = [random.random() for i in range(25)]


aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()

datax = [random.random() for i in range(25)]
datay = [random.random() for i in range(25)]