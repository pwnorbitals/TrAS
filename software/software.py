from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
import pyvo
import math
import threading
import jiulian as jd
import computations as comp
matplotlib.use('Qt5Agg')

from PyQt5.QtSql import QSqlTableModel
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, 
    QTextEdit, QGridLayout, QApplication, QGroupBox, QVBoxLayout, QWidget, QSlider, QFileDialog, QDialog, QDialogButtonBox,
    QTableView, QComboBox, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtGui import QDoubleValidator

from numpy import arange, sin, pi, std
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import linregress
from datetime import datetime
import matplotlib as mpl
from matplotlib.widgets import Slider
from math import floor

from scipy.ndimage import gaussian_filter1d


plt.style.use('ggplot')
plt.rcParams["font.size"] = 6
mpl.rcParams['toolbar'] = 'None'
progname = os.path.basename(sys.argv[0])
service = pyvo.dal.TAPService("http://voparis-tap-planeto.obspm.fr/tap")


def getInfo(name):
    query = "SELECT * FROM exoplanet.epn_core WHERE target_name ILIKE '%"+name+"%'"
    results = service.search(query)
    return results
    
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

def smooth(inlist, param):
    return gaussian_filter1d(inlist, param)



class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("About")
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.label = QLabel("Built by Chris de CLAVERIE, Magdalena CALKA and William BOITIER!\n\nIPSA CIRI Exoplanet Transits 2020")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class SettingsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("Settings")
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        unitsBox = QGroupBox("Units")
        unitsLayout = QFormLayout()
        unitsBox.setLayout(unitsLayout)

        lengthLabel = QLabel("Length unit : ")
        lengthBox = QComboBox()
        lengthBox.addItems(["Kilometer (km)", "Jupiter radius (RJ)", "Sun radius (RS)", "Astronomical unit (AU)"])
        unitsLayout.addRow(lengthLabel, lengthBox)

        massLabel = QLabel("Mass unit : ")
        massBox = QComboBox()
        massBox.addItems(["Kilogram (kg)", "Tonnes (T)", "Jupiter mass (MJ)", "Sun mass (MS)"])
        unitsLayout.addRow(massLabel, massBox)

        timeLabel = QLabel("Time unit : ")
        timeBox = QComboBox()
        timeBox.addItems(["Second (s)", "Day", "Year"])
        unitsLayout.addRow(timeLabel, timeBox)

        angleLabel = QLabel("Angles unit : ")
        angleBox = QComboBox()
        angleBox.addItems(["Radians (rad)", "Regrees (deg)"])
        unitsLayout.addRow(angleLabel, angleBox)

        layout = QVBoxLayout()
        layout.addWidget(unitsBox)
        layout.addWidget(buttonBox)
        self.setLayout(layout)


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#f0f0f0")
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
        self.file_menu.addAction('&Open', self.openFile,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('&Settings', self.openSettings,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_U)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.help_menu.addAction('&About', self.About)
        self.menuBar().addMenu(self.help_menu)

        self.main_widget = QtWidgets.QWidget(self)

        
        self.setGeometry(50, 50, 1200, 800)
        self.setWindowTitle('Review')    
        

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        grid = QGridLayout(self.main_widget)
        grid.addWidget(self.GroupGraph(), 0,0)
        grid.addLayout(self.GroupResult(),0,1)
        grid.addWidget(self.GroupDataBase(),0,2)
        grid.setSpacing(10)

        self.k = 8
        self.a = 0
        self.b = 0

        self.Star_Radius = 1.0
        self.Period = 1.0

        self.Y="V-C"
        
    def About(self):
        dlg = AboutDialog(self)
        dlg.exec_()

    def openFile(self):
        file = QFileDialog.getOpenFileName(self, 'Open File')
        if file[0]:
            aw.setWindowTitle("%s [%s]" % (progname, file[0]))
            # Parse file
            file = open(file[0], 'r')
            lines = file.readlines()
            file.close()
            try:
                self.lines = [line[:-1].split(' ') for line in lines]
                self.parseData()
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Could not load the selected file")
                msg.setInformativeText("The file you tried to open is not in the right format.\n\nException : " + str(e))
                msg.setWindowTitle("Open exception")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def openSettings(self):
        dlg = SettingsDialog(self)
        dlg.exec_()

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
        self.dataCanvas.axes.plot(timestamps, [float(d) for d in VC], linewidth=1.0)

        # Compute standard errors (use tunable parameter)
        errors = []
        for i in range(len(VC)):
            #vals = [float(getVal(i + j, VC)) for j in range(-nb_vals, +nb_vals)]
            vals = windowAround(VC, i, nb_vals)
            errors.append(std(vals))

            #print(errors)
        errors_smoothed = smooth(errors, nb_vals)
        self.errorCanvas.axes.clear()
        self.errorCanvas.axes.set_title('Standard errors')
        self.errorCanvas.axes.plot(timestamps, errors_smoothed, linewidth=1.0)

        # Find local maxima
        peaks, properties = find_peaks(errors_smoothed, prominence=10**(-self.prominence))
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
        # Menu deroulant
        self.MenuS = QComboBox(self)
        self.MenuS.textActivated.connect(self.RefStarChanged)
        
        labelMenuS = QtWidgets.QLabel()
        labelMenuS.setText("Reference Star")

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
        tuto2 = "\n\nThe s coefficient is the number of samples used to smooth the data.\n\n\n"
        labeltuto = QLabel(tuto1+tuto2)

        self.labelInfoP = QtWidgets.QLabel()
        self.labelInfoP.setText('The prominence value changes the sensitivity of peak detection on the errors graph : ')

        self.validator = QDoubleValidator()
        self.RS_input = QLineEdit()
        self.RS_input.setValidator(self.validator)
        self.RS_input.returnPressed.connect(self.RadiusChanged)
        
        self.Per_input = QLineEdit()
        self.Per_input.setValidator(self.validator)
        self.Per_input.returnPressed.connect(self.PeriodChanged)

        self.s = 2
        sliderS = QSlider(Qt.Horizontal)
        sliderS.setFocusPolicy(Qt.StrongFocus)
        sliderS.setTickPosition(QSlider.TicksBothSides)
        sliderS.setTickInterval(10)
        sliderS.setSingleStep(1)
        sliderS.setMinimum(1)
        sliderS.valueChanged.connect(self.changeS)
        self.ss = sliderS
        sliderS.setValue(self.s)

        self.k = 8
        sliderK = QSlider(Qt.Horizontal)
        sliderK.setFocusPolicy(Qt.StrongFocus)
        sliderK.setTickPosition(QSlider.TicksBothSides)
        sliderK.setTickInterval(10)
        sliderK.setSingleStep(1)
        sliderK.setMinimum(2)
        sliderK.valueChanged.connect(self.changeK)
        self.sk = sliderK
        sliderK.setValue(self.k)

        self.prominence = 8
        sliderP = QSlider(Qt.Horizontal)
        sliderP.setFocusPolicy(Qt.StrongFocus)
        sliderP.setTickPosition(QSlider.TicksBothSides)
        sliderP.setTickInterval(10)
        sliderP.setSingleStep(1)
        sliderP.valueChanged.connect(self.changeP)
        self.sp = sliderP
        sliderP.setValue(self.prominence)

        self.a = 0
        sliderA = QSlider(Qt.Horizontal)
        sliderA.setFocusPolicy(Qt.StrongFocus)
        sliderA.setTickPosition(QSlider.TicksBothSides)
        sliderA.setTickInterval(10)
        sliderA.setSingleStep(1)
        sliderA.valueChanged.connect(self.changeA)
        self.sa = sliderA
        sliderA.setValue(self.a)

        self.b = 0
        sliderB = QSlider(Qt.Horizontal)
        sliderB.setFocusPolicy(Qt.StrongFocus)
        sliderB.setTickPosition(QSlider.TicksBothSides)
        sliderB.setTickInterval(10)
        sliderB.setSingleStep(1)
        sliderB.valueChanged.connect(self.changeB)
        sliderB.setInvertedAppearance(True)
        self.sb = sliderB
        sliderB.setValue(self.b)

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
        
        groupBoxCalculations = QGroupBox('Calculations')
        calbox = QVBoxLayout()
        calbox.addLayout(GridResult)
        calbox.addStretch(1)
        groupBoxCalculations.setLayout(calbox)
        
        groupBoxResult = QGroupBox('Settings')
        vbox = QVBoxLayout()
        vbox.addWidget(labelMenuS)
        vbox.addWidget(self.MenuS)
        vbox.addWidget(self.labelInfosK)
        vbox.addWidget(sliderK)
        vbox.addWidget(self.labelInfosS)
        vbox.addWidget(sliderS)
        vbox.addWidget(self.labelInfoP)
        vbox.addWidget(sliderP)
        vbox.addWidget(labelInfosA)
        vbox.addLayout(hbox)
        vbox.addWidget(labeltuto)
        vbox.addStretch(1)
        groupBoxResult.setLayout(vbox)       

        ret = QVBoxLayout()
        ret.addWidget(groupBoxResult)
        ret.addWidget(groupBoxCalculations)
        
        return ret
    
    def GroupDataBase(self):
        labelName = QtWidgets.QLabel()
        labelName.setText("Exoplanet Name:          ")

        self.NP_input = QLineEdit()
        self.NP_input.returnPressed.connect(self.onResearchClick)

        self.buttonS = QPushButton('Search', self)
        self.buttonS.setToolTip('Search')
        self.buttonS.clicked.connect(self.onResearchClick)

        self.MenuD = QComboBox(self)

        self.labelMenuD = QtWidgets.QLabel()
        self.labelMenuD.setText("Result choice : ")

        self.buttonImport = QPushButton('Import', self)
        self.buttonImport.setToolTip('Import')
        self.buttonImport.clicked.connect(self.importSelection)


        groupBoxDataBase = QGroupBox('Import Data')
        hbox = QVBoxLayout()
        hbox.addWidget(labelName)
        hbox.addWidget(self.NP_input)
        hbox.addWidget(self.buttonS)
        hbox.addWidget(self.labelMenuD)
        hbox.addWidget(self.MenuD)
        hbox.addWidget(self.buttonImport)

        hbox.addStretch(1)
        groupBoxDataBase.setLayout(hbox)



        return groupBoxDataBase


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

    def changeP(self):
        self.p = self.sp.value()
        self.compute_figures()

    def compute_figures(self):
        try:
            self.parseData()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Could not compute the data")
            msg.setInformativeText("An error occurred when trying to compute the data.\n\nException : " + str(e))
            msg.setWindowTitle("Internal error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        
    
    def onResearchClick(self):
        self.searchval = self.NP_input.text()
        if(len(self.searchval) < 3):
            print("NO")
            return
        threading.Thread(target=self.doResearch).start()
        self.buttonS.setText("Search (loading)")
        
    
    def doResearch(self):
        try:
            self.results = getInfo(self.searchval)
            self.buttonS.setText("Search")
            if self.results:
                names = [i.get('target_name').decode("utf-8")  for i in self.results]
                self.labelMenuD.setText("Result choice ("+str(len(self.results))+" results): ")
                self.MenuD.clear()
                self.MenuD.addItems(names)
        except Exception as e:
            self.buttonS.setText("Search (failed)")
            
        
    def ChoiceOfStar(self):
        self.MenuS.clear()
        self.MenuS.addItems(self.ListRefStar)
        
       
    def RefStarChanged(self):
        self.Y = str(self.MenuS.currentText())
        self.compute_figures()

    def importSelection(self):
        index = self.MenuD.currentIndex()
        entry = self.results[index]
        self.RS_input.setText(str(entry.get('star_radius')))
        self.Per_input.setText(str(entry.get('period')))
        print(entry.get('star_radius'), entry.get('period'))


qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())