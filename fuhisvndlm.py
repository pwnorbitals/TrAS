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

progname = os.path.basename(sys.argv[0])



class data(object):
	def __init__(self):
		self.dataX = dataX
		self.dataY = dataY
		self.processDataX = processDataX
		self.processDataY = processDataY
		self.repertory = repertory
    

	def csvRead(self):
		pass

	def lissage(self):
    #moving average + taff willy
		pass

	def truc_De_Chris(self):
	#traitement des données
		pass



class Canvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig = fig
        self.axes = fig.add_subplot(111)
        super(Canvas, self).__init__(fig)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)




class RawDataCanvas(Canvas,data):
    """Simple canvas with a sine plot."""
    
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.cla()
        self.axes.plot(t, s)
        self.axes.set_title('Raw data')
    
    def compute_figure(self, a):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t*a)
        self.axes.clear()
        self.axes.plot(t, s)
        self.axes.set_title('Raw data')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

class ProcessDataCanvas(Canvas,data):

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)
        self.axes.set_title('Process data')

    def compute_figure(self, k):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t*k)
        self.axes.clear()
        self.axes.plot(t, s)
        self.axes.set_title('Process data')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


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
        

    def OpenFile(self):
        file = QFileDialog.getOpenFileName(self, 'Open File')
        if file[0]:
            f = open(file[0], 'r')

            with f:
                data = f.read()

        print(data)


    def GroupGraph(self):
         #graphics and toolbars        
        Rd = RawDataCanvas(self.main_widget, width=5, height=5, dpi=100)
        self.rd = Rd
        Cd = ProcessDataCanvas(self.main_widget, width=5, height=5, dpi=100)
        self.cd = Cd
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
        sliderK.valueChanged.connect(self.changeK)
        self.sk = sliderK

        sliderA = QSlider(Qt.Horizontal)
        sliderA.setFocusPolicy(Qt.StrongFocus)
        sliderA.setTickPosition(QSlider.TicksBothSides)
        sliderA.setTickInterval(10)
        sliderA.setSingleStep(1)
        sliderA.valueChanged.connect(self.changeA)
        self.sa = sliderA

        groupBoxResult = QGroupBox('Results')
        vbox = QVBoxLayout()
        vbox.addWidget(labelResult)
        vbox.addWidget(labelInfosK)
        vbox.addWidget(sliderK)
        vbox.addWidget(labelInfosA)
        vbox.addWidget(sliderA)
        vbox.addStretch(1)
        groupBoxResult.setLayout(vbox)       
        
        return groupBoxResult


    def fileQuit(self):
        self.close()


    def changeA(self, a_in):
        self.rd.compute_figure(self.sa.value())

    def changeK(self, k_in):
        self.cd.compute_figure(self.sk.value())

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