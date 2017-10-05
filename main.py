#!/usr/bin/env python

import sys
import src.mainwindow as mw
from PyQt4 import QtGui
from PyQt4 import QtCore

if __name__ == "__main__":
    # Start Qt Application
    app = QtGui.QApplication(sys.argv)
    main_window = mw.PlotWindow()
    main_window.show()
    # Enter the main loop
    app.exec_()
