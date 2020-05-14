from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QFormLayout, QComboBox, QGroupBox
from PyQt5.QtCore import QSettings

class SettingsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("Settings")
        self.index = [0,0,0,0]
        self.restoreSettings()

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        unitsBox = QGroupBox("Units")
        unitsLayout = QFormLayout()
        unitsBox.setLayout(unitsLayout)

        lengthLabel = QLabel("Length unit : ")
        self.lengthBox = QComboBox()
        self.lengthBox.addItems(["Kilometer (km)", "Jupiter radius (RJ)", "Sun radius (RS)", "Astronomical unit (AU)"])
        self.lengthBox.setCurrentIndex(self.index[0])
        unitsLayout.addRow(lengthLabel, self.lengthBox)

        massLabel = QLabel("Mass unit : ")
        self.massBox = QComboBox()
        self.massBox.addItems(["Kilogram (kg)", "Tonnes (T)", "Jupiter mass (MJ)", "Sun mass (MS)"])
        self.massBox.setCurrentIndex(self.index[1])
        unitsLayout.addRow(massLabel, self.massBox)

        timeLabel = QLabel("Time unit : ")
        self.timeBox = QComboBox()
        self.timeBox.addItems(["Second (s)", "Day", "Year"])
        self.timeBox.setCurrentIndex(self.index[2])
        unitsLayout.addRow(timeLabel, self.timeBox)

        angleLabel = QLabel("Angles unit : ")
        self.angleBox = QComboBox()
        self.angleBox.addItems(["Radians (rad)", "Degrees (deg)"])
        self.angleBox.setCurrentIndex(self.index[3])
        unitsLayout.addRow(angleLabel, self.angleBox)

        layout = QVBoxLayout()
        layout.addWidget(unitsBox)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        self.restoreSettings()

    def accept(self):
        conv_len = self.lengthBox.currentText()
        conv_mass = self.massBox.currentText()
        conv_time = self.timeBox.currentText()
        conv_angle = self.angleBox.currentText()
        self.index = [self.lengthBox.currentIndex(),self.massBox.currentIndex(),self.timeBox.currentIndex(),self.angleBox.currentIndex()]
        self.close()
        return [conv_len, conv_mass, conv_time, conv_angle]

    def closeEvent(self, event):
        self.saveSettings()
        super(SettingsDialog, self).closeEvent(event)

    def saveSettings(self):
        settings = QSettings("IPSA", "ciri")
        settings.setValue('index', self.index)

    def restoreSettings(self):
        settings = QSettings("IPSA", "ciri")
        self.index = list(map(int, settings.value('index')))