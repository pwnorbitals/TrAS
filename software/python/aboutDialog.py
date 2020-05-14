from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

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