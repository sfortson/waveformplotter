#!/usr/bin/env python

import sys

from PyQt6.QtWidgets import QApplication

import widgets.mainwindow as mw

if __name__ == "__main__":
    # Start Qt Application
    app = QApplication(sys.argv)
    main_window = mw.PlotWindow()
    main_window.show()
    # Enter the main loop
    app.exec()
