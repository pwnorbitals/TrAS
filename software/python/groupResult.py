from PyQt5.QtWidgets import QComboBox, QLabel, QSlider, QLineEdit, QHBoxLayout, QGridLayout, QGroupBox, QVBoxLayout
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import canvas

def GroupResult(self):
        # Menu deroulant
        self.MenuS = QComboBox(self)
        self.MenuS.textActivated.connect(self.RefStarChanged)
        
        labelMenuS = QLabel()
        labelMenuS.setText("Reference Star")

        self.labelRadius = QLabel()
        self.labelRadius.setText("Enter the Star's radius (%s):"% self.str_conv[0])

        self.labelPeriod = QLabel()
        self.labelPeriod.setText("Enter the Period of orbit (%s):"%self.str_conv[2])

        self.PlanetLabel = QLabel('Planet radius : \nPlanet mass : ')
        self.StarLabel = QLabel('Star density : \nStar mass : ')
        self.Other = QLabel('Impact parameter b : \nSemimajor axis a : \nInclinaison : ')
        self.LC = QLabel('Depth : \nTotal duration : \nFull duration : ')

        self.labelInfosK = QLabel('Change the K coefficient :  (note: coeff was calculated to be optimal)')

        self.labelInfosS = QLabel('Change the s coefficient : ')

        labelInfosA = QLabel()
        labelInfosA.setText('Change boundary values from left and right :')

        tuto1 = "The K coefficient characterize the time's interval used for error calculation.\nIncrease K implies less approximation segments."
        tuto2 = "\n\nThe s coefficient is the number of samples used to smooth the data.\n\n\n"
        labeltuto = QLabel(tuto1+tuto2)

        self.labelInfoP = QLabel()
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

        hbox = QHBoxLayout()
        hbox.addWidget(sliderA)
        hbox.addWidget(sliderB)

        GridResult = QGridLayout()
        #User Input
        GridResult.addWidget(self.labelRadius, 0,0)
        GridResult.addWidget(self.RS_input, 1,0)
        GridResult.addWidget(self.labelPeriod, 0,1)
        GridResult.addWidget(self.Per_input, 1,1)
        
        #Deduced Parameter
        GridResult.addWidget(self.PlanetLabel, 2,0)
        GridResult.addWidget(self.StarLabel, 3,0)
        GridResult.addWidget(self.LC, 2,1)
        GridResult.addWidget(self.Other, 3,1)

        #Analytical light curve
        Th = canvas.Canvas(self.main_widget, width=5, height=5, dpi=100)
        self.theoricCanvas = Th
        toolbarTh = NavigationToolbar(Th, self)
        
        groupBoxCalculations = QGroupBox('Calculations')
        calbox = QVBoxLayout()
        calbox.addLayout(GridResult)
        calbox.addStretch(1)
        calbox.addWidget(toolbarTh)
        calbox.addWidget(Th)
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