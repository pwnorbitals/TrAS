# Copyright 2020 de Claverie Chris
# Copyright 2020 Calka Magdalena
# Copyright 2020 Boitier William


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
import os
import sys

import appWindow

scriptDir = os.path.dirname(os.path.realpath(__file__))
progname = os.path.basename(sys.argv[0])

qApp = QtWidgets.QApplication(sys.argv)

aw = appWindow.ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.setWindowIcon(QIcon(scriptDir + os.path.sep + '..' + os.path.sep + 'img' + os.path.sep + 'LOGO6.png'))
aw.show()
sys.exit(qApp.exec_())
