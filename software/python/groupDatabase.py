from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QGroupBox, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
import threading
import pyvo
import os

scriptDir = os.path.dirname(os.path.realpath(__file__))
exoplanet = pyvo.dal.TAPService("http://voparis-tap-planeto.obspm.fr/tap")

def GroupDataBase(self):
        labelName = QLabel()
        labelName.setText("Exoplanet Name:          ")

        self.NP_input = QLineEdit()
        self.NP_input.returnPressed.connect(lambda : onResearchClick(self))

        self.buttonS = QPushButton('Search', self)
        self.buttonS.setToolTip('Search')
        self.buttonS.clicked.connect(lambda : onResearchClick(self))

        self.MenuD = QComboBox(self)

        self.labelMenuD = QLabel()
        self.labelMenuD.setText("Result choice : ")

        self.buttonImport = QPushButton('Import', self)
        self.buttonImport.setToolTip('Import')
        self.buttonImport.clicked.connect(lambda : importSelection(self))

        pic = QLabel(self)
        pic.setPixmap(QPixmap(scriptDir + os.path.sep + '..' + os.path.sep + 'img' + os.path.sep + 'LOGO5.png').scaled(200, 200))
        pic.setAlignment(QtCore.Qt.AlignCenter)


        groupBoxDataBase = QGroupBox('Import Data')
        hbox = QVBoxLayout()
        hbox.addWidget(labelName)
        hbox.addWidget(self.NP_input)
        hbox.addWidget(self.buttonS)
        hbox.addWidget(self.labelMenuD)
        hbox.addWidget(self.MenuD)
        hbox.addWidget(self.buttonImport)
        hbox.addStretch()
        hbox.addWidget(pic)
        groupBoxDataBase.setLayout(hbox)



        return groupBoxDataBase

def onResearchClick(self):
        self.searchval = self.NP_input.text()
        if(len(self.searchval) < 3):
            print("NO")
            return
        threading.Thread(target=lambda: doResearch(self)).start()
        self.buttonS.setText("Search (loading)")
        
def doResearch(self):
    try:
        query = "SELECT * FROM exoplanet.epn_core WHERE target_name ILIKE '%"+self.searchval+"%'"
        self.results = exoplanet.search(query)
        self.buttonS.setText("Search")
        if self.results:
            names = [i.get('target_name').decode("utf-8")  for i in self.results]
            self.labelMenuD.setText("Result choice ("+str(len(self.results))+" results): ")
            self.MenuD.clear()
            self.MenuD.addItems(names)
    except Exception as e:
        self.buttonS.setText("Search (failed : " + str(e) + ")")

def importSelection(self):
    index = self.MenuD.currentIndex()
    entry = self.results[index]
    self.RS_input.setText(str(entry.get('star_radius')))
    self.Per_input.setText(str(entry.get('period')))
    print(entry.get('star_radius'), entry.get('period'))

    self.str_conv[0] = "RS"
    self.str_conv[2] = "Day"
    self.conversion[0] = 1/696342
    self.conversion[2] = 1/86400
    self.compute_figures()