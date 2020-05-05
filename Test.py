import sys
from PyQt5.QtWidgets import QApplication, QCheckBox

app = QApplication.instance() 
if not app:
    app = QApplication(sys.argv)

# création de la case à cocher
case = QCheckBox("Voici ma premiere case a cocher")

# la case à cocher est rendue visible
case.show()

app.exec_()