# Basic packages
from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
import pyvo
import math
import threading

# PyQT
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLabel, QLineEdit, 
    QGridLayout, QGroupBox, QVBoxLayout, QSlider, QFileDialog, 
    QComboBox, QPushButton, QMessageBox)
from PyQt5.QtGui import QDoubleValidator



# Matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar



# Local files
import aboutDialog
import settingsDialog
import canvas
import parseData


# Settings
matplotlib.use('Qt5Agg')
plt.style.use('ggplot')
plt.rcParams["font.size"] = 6
mpl.rcParams['toolbar'] = 'None'
progname = os.path.basename(sys.argv[0])
service = pyvo.dal.TAPService("http://voparis-tap-planeto.obspm.fr/tap")


# Helper functions
    # Retrieve data from exoplanet.eu
def getInfo(name):
    query = "SELECT * FROM exoplanet.epn_core WHERE target_name ILIKE '%"+name+"%'"
    results = service.search(query)
    return results
    


# Main application window
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Open', self.openFile,
                                 Qt.CTRL + Qt.Key_O)
        self.file_menu.addAction('&Settings', self.openSettings,
                                 Qt.CTRL + Qt.Key_U)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 Qt.CTRL +Qt.Key_Q)
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

        self.Star_Radius = 1.0
        self.Period = 1.0

        self.Y="V-C"
        
    def About(self):
        dlg = aboutDialog.AboutDialog(self)
        dlg.exec_()

    def openFile(self):
        file = QFileDialog.getOpenFileName(self, 'Open File')
        if file[0]:
            self.setWindowTitle("%s [%s]" % (progname, file[0]))
            # Parse file
            file = open(file[0], 'r')
            lines = file.readlines()
            file.close()
            try:
                self.lines = [line[:-1].split(' ') for line in lines]
                parseData.parseData(self)
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Could not load the selected file")
                msg.setInformativeText("The file you tried to open is not in the right format.\n\nException : " + str(e))
                msg.setWindowTitle("Open exception")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def openSettings(self):
        dlg = settingsDialog.SettingsDialog(self)
        dlg.exec_()

    def GroupGraph(self):
         #graphics and toolbars        
        Rd = canvas.Canvas(self.main_widget, width=5, height=5, dpi=100)
        self.dataCanvas = Rd
        Cd = canvas.Canvas(self.main_widget, width=5, height=5, dpi=100)
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

        sliderS = QSlider(Qt.Horizontal)
        sliderS.setFocusPolicy(Qt.StrongFocus)
        sliderS.setTickPosition(QSlider.TicksBothSides)
        sliderS.setTickInterval(10)
        sliderS.setSingleStep(1)
        sliderS.setMinimum(1)
        sliderS.valueChanged.connect(self.compute_figures)
        self.ss = sliderS
        sliderS.setValue(2)

        sliderK = QSlider(Qt.Horizontal)
        sliderK.setFocusPolicy(Qt.StrongFocus)
        sliderK.setTickPosition(QSlider.TicksBothSides)
        sliderK.setTickInterval(10)
        sliderK.setSingleStep(1)
        sliderK.setMinimum(2)
        sliderK.valueChanged.connect(self.compute_figures)
        self.sk = sliderK
        sliderK.setValue(8)

        sliderP = QSlider(Qt.Horizontal)
        sliderP.setFocusPolicy(Qt.StrongFocus)
        sliderP.setTickPosition(QSlider.TicksBothSides)
        sliderP.setTickInterval(10)
        sliderP.setSingleStep(1)
        sliderP.valueChanged.connect(self.compute_figures)
        self.sp = sliderP
        sliderP.setValue(8)

        sliderA = QSlider(Qt.Horizontal)
        sliderA.setFocusPolicy(Qt.StrongFocus)
        sliderA.setTickPosition(QSlider.TicksBothSides)
        sliderA.setTickInterval(10)
        sliderA.setSingleStep(1)
        sliderA.valueChanged.connect(self.compute_figures)
        self.sa = sliderA
        sliderA.setValue(0)

        sliderB = QSlider(Qt.Horizontal)
        sliderB.setFocusPolicy(Qt.StrongFocus)
        sliderB.setTickPosition(QSlider.TicksBothSides)
        sliderB.setTickInterval(10)
        sliderB.setSingleStep(1)
        sliderB.valueChanged.connect(self.compute_figures)
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

    def compute_figures(self):
        try:
            parseData.parseData(self)
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

