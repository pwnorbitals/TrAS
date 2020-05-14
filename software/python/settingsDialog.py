from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QFormLayout, QComboBox, QGroupBox

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
        angleBox.addItems(["Radians (rad)", "Degrees (deg)"])
        unitsLayout.addRow(angleLabel, angleBox)

        layout = QVBoxLayout()
        layout.addWidget(unitsBox)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def accept(self):