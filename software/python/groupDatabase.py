# Copyright 2020 de Claverie Chris
# Copyright 2020 Calka Magdalena
# Copyright 2020 Boitier William


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
        pic.setPixmap(QPixmap(scriptDir + os.path.sep + '..' + os.path.sep + 'img' + os.path.sep + 'LOGO6.png').scaled(200, 200))
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
    self.SRadius.value = entry.get('star_radius') * 695700
    self.PPeriod.value = entry.get('period') * (60*60*24)
    self.SRadius._combo.setCurrentIndex(self.SRadius._combo.findText('Rs'))
    self.PPeriod._combo.setCurrentIndex(self.PPeriod._combo.findText('day'))
    print(entry.get('star_radius'), entry.get('period'))

    self.compute_figures()