# Basic packages
from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
import math

# PyQT
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QGridLayout, QGroupBox, QVBoxLayout, QLineEdit, QPushButton, QComboBox, QFileDialog


# Matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Local files
import aboutDialog
import settingsDialog
import canvas
import parseData
import groupResult
import groupDatabase

# Settings
matplotlib.use('Qt5Agg')
plt.style.use('ggplot')
plt.rcParams["font.size"] = 6
mpl.rcParams['toolbar'] = 'None'

   

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
        grid.addLayout(groupResult.GroupResult(self),0,1)
        grid.addWidget(groupDatabase.GroupDataBase(self),0,2)
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
            self.setWindowTitle("%s [%s]" % (os.path.basename(sys.argv[0]), file[0]))
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
            
    def ChoiceOfStar(self):
        self.MenuS.clear()
        self.MenuS.addItems(self.ListRefStar)
       
    def RefStarChanged(self):
        self.Y = str(self.MenuS.currentText())
        self.compute_figures()

   

