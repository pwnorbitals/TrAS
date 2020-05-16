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