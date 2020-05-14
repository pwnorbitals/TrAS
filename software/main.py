from PyQt5 import QtCore, QtWidgets
import os
import sys

import appWindow

progname = os.path.basename(sys.argv[0])

qApp = QtWidgets.QApplication(sys.argv)

aw = appWindow.ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())