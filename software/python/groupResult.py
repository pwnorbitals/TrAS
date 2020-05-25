from PyQt5.QtWidgets import QComboBox, QLabel, QSlider, QLineEdit, QHBoxLayout, QGridLayout, QGroupBox, QVBoxLayout
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from enum import Enum, auto

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import canvas

MassUnits = {
        'Kg': 1,
        'T': 1/1000,
        'Mj': 1/(1.89813e27),
        'Ms': 1/(1.9884e30) 
}

AngleUnits = {
        'Deg': 180/3.14159265,
        'rad': 1
}

LengthUnits = {
        'm': 1000,
        'Km': 1,
        'Rs': 1/695700,
        'Rj': 1/71492,
        'UA': 1/(1.5e8)
}

TimeUnits = {
        's': 1,
        'min': 1/60,
        'h': 1/(60*60),
        'day': 1/(60*60*24),
        'year': 1/(60*60*24*365)
}

DensityUnits = {
        'kg/m3': 1
}

NoneUnits = { 'None': 1}

class Dimension(Enum):
        LENGTH = auto(),
        MASS = auto(),
        TIME = auto(),
        DENSITY = auto(),
        ANGLE = auto(),
        NONE = auto()

DimensionMap = {
        Dimension.LENGTH: LengthUnits,
        Dimension.MASS: MassUnits,
        Dimension.TIME: TimeUnits,
        Dimension.NONE: NoneUnits,
        Dimension.DENSITY: DensityUnits,
        Dimension.ANGLE : AngleUnits
}

class ResultField():
        def convert(self):
                factor = DimensionMap[self._dim][self._combo.currentText()]
                converted = self._value*factor
                self._valLabel.setText(str(converted))

        def __init__(self, dimension:Dimension, label):
                self._value = 0
                self._label = QLabel(label)
                self._valLabel = QLabel()
                self._dim = dimension
                self._combo = QComboBox()
                self._combo.addItems(list(DimensionMap[self._dim].keys()))
                self._combo.activated.connect(self.convert)

        @property
        def value(self):
                return self._value
        
        @value.setter
        def value(self, newvalue):
                self._value = newvalue
                self.convert()


        @property
        def dim(self):
                return self._dim

        @value.setter
        def dim(self, newdim:Dimension):
                self._dim = newdim
                self._combo.clear()
                self._combo.addItems(list(DimensionMap[self._dim].keys()))

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

        self.PRadius = ResultField(Dimension.LENGTH, 'Planet radius :')
        self.PMass = ResultField(Dimension.MASS, 'Planet mass :')
        self.PlanetLayout = QGridLayout()
        self.PlanetLayout.addWidget(self.PRadius._label, 0, 1)
        self.PlanetLayout.addWidget(self.PRadius._valLabel, 0, 2)
        self.PlanetLayout.addWidget(self.PRadius._combo, 0, 3)
        self.PlanetLayout.addWidget(self.PMass._label, 1, 1)
        self.PlanetLayout.addWidget(self.PMass._valLabel, 1, 2)
        self.PlanetLayout.addWidget(self.PMass._combo, 1, 3)

        self.SDensity = ResultField(Dimension.DENSITY, 'Star density : ')
        self.SMass = ResultField(Dimension.MASS, 'Star mass : ')
        self.StarLayout = QGridLayout()
        self.StarLayout.addWidget(self.SDensity._label, 0, 1)
        self.StarLayout.addWidget(self.SDensity._valLabel, 0, 2)
        self.StarLayout.addWidget(self.SDensity._combo, 0, 3)
        self.StarLayout.addWidget(self.SMass._label, 1, 1)
        self.StarLayout.addWidget(self.SMass._valLabel, 1, 2)
        self.StarLayout.addWidget(self.SMass._combo, 1, 3)


        self.ImpParameter = ResultField(Dimension.NONE, 'Impact parameter :')
        self.SMA = ResultField(Dimension.LENGTH, 'Semi-major axis : ')
        self.inc = ResultField(Dimension.NONE, 'Inclination : ')
        self.OtherLayout = QGridLayout()
        self.OtherLayout.addWidget(self.ImpParameter._label, 0, 1)
        self.OtherLayout.addWidget(self.ImpParameter._valLabel, 0, 2)
        self.OtherLayout.addWidget(self.ImpParameter._combo, 0, 3)
        self.OtherLayout.addWidget(self.inc._label, 1, 1)
        self.OtherLayout.addWidget(self.inc._valLabel, 1, 2)
        self.OtherLayout.addWidget(self.inc._combo, 1, 3)
        self.OtherLayout.addWidget(self.SMA._label, 2, 1)
        self.OtherLayout.addWidget(self.SMA._valLabel, 2, 2)
        self.OtherLayout.addWidget(self.SMA._combo, 2, 3)


        self.depth = ResultField(Dimension.NONE, 'Depth :')
        self.TotalDuration = ResultField(Dimension.TIME, 'Total duration :')
        self.FullDuration = ResultField(Dimension.TIME, 'Full duration :')
        self.LCLayout = QGridLayout()
        self.LCLayout.addWidget(self.depth._label, 0, 1)
        self.LCLayout.addWidget(self.depth._valLabel, 0, 2)
        self.LCLayout.addWidget(self.depth._combo, 0, 3)
        self.LCLayout.addWidget(self.TotalDuration._label, 1, 1)
        self.LCLayout.addWidget(self.TotalDuration._valLabel, 1, 2)
        self.LCLayout.addWidget(self.TotalDuration._combo, 1, 3)
        self.LCLayout.addWidget(self.FullDuration._label, 2, 1)
        self.LCLayout.addWidget(self.FullDuration._valLabel, 2, 2)
        self.LCLayout.addWidget(self.FullDuration._combo, 2, 3)




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
        GridResult.addLayout(self.PlanetLayout, 2,0)
        GridResult.addLayout(self.StarLayout, 3,0)
        GridResult.addLayout(self.LCLayout, 2,1)
        GridResult.addLayout(self.OtherLayout, 3,1)

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