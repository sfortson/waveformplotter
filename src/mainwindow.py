#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
import PyQt4.Qwt5 as Qwt

class SetYLimWidget(QtGui.QWidget):

    def __init__(self, widget_parent = None):
        # Init the base class
        QtGui.QWidget.__init__(self, widget_parent)

        # Set the Widgets
        self.init_widgets()

    def init_widgets(self):
        # Init the layout and widgets
        hbox = QtGui.QHBoxLayout(self)
        label = QtGui.QLabel("Set y-limit:")
        self.line = QtGui.QLineEdit()
        button = QtGui.QPushButton("Set")

        # Set default line edit text
        self.line.setText("0")

        # Add widgets to the layout
        hbox.addWidget(label)
        hbox.addWidget(self.line)
        hbox.addWidget(button)

        # Set this widget's layout to hbox
        self.setLayout(hbox)

        # Connect set button
        button.clicked.connect(self.set_button_clicked)

    def set_button_clicked(self):
        # Slot controlling what happens when set button is clicked, 
        # or Enter key is pressed
        lineValue = self.get_line_value()
        self.emit(QtCore.SIGNAL("SetClicked"), lineValue)

    def get_line_value(self):
        # Return the integer value of what the user entered in the line edit
        return int(self.line.text())

    def set_line_value(self, yMax):
        # Set line edit value to yMax
        self.line.setText(QtCore.QString(yMax))

    def keyPressEvent(self, event):
        # Allow the user to hit enter when setting y-limit
        if event.matches(QtGui.QKeySequence.InsertParagraphSeparator):
            self.set_button_clicked()

class CentralWidget(QtGui.QWidget):

    def __init__(self, widget_parent = None):
        # Init the base class
        QtGui.QWidget.__init__(self, widget_parent)

        # Define class variables
        self.init_class_variables()
        self.yMax = 0
        self.yMin = 0

        # Set the minimum size and layout
        self.setMinimumSize(750, 250)
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

    def get_file_info(self, filenames):
        import sacfilereader
        data = sacfilereader.sac_reader(filenames)
        return data

    def new_plot(self, fileName):
        # Read data from the SAC file and update the plot widget
        data = self.get_file_info(str(fileName))
        newplot = PlotWidget(data, self)

        # Set plot text displaying the sac file 
        newplot.plot_label(fileName)

        # Add plot widget to plot list and layout
        self.plot.append(newplot)
        self.grid.addWidget(newplot, len(self.plot), 0, 1, 4)
        
        # Update the class variables that hold the minimum and 
        # maximum x-values with the new values found from
        # adding this new data
        self.sync_axes(round(data[1] + len(data[0]) * data[2]),
                data[1])
        
        # Call the function to sync or not based on user input
        self.sync_toggled(self.parentWidget().sync_is_checked())

    def add_plot(self):
        # Get a file from the user and add that file to the label of files
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                "Open SAC File", ".", "SAC Files (*.sac *.SAC *.*)")
        if fileName:
            self.new_plot(fileName)
       
    def sync_toggled(self, checked):
        # What to do if sync is toggled on or off
        if checked:
            if self.yMin == 0 and self.yMax == 0:
                for p in self.plot:
                    p.set_axes_semi_auto(self.xMin, self.xMax, 
                            Qwt.QwtPlot.xBottom, Qwt.QwtPlot.yLeft)
            else:
                for p in self.plot:
                    p.set_axes(self.xMax, self.xMin, self.yMax, self.yMin)
            p.get_zoomer().setZoomBase()
#                p.bottom_plot(False)
#            self.plot[-1].bottom_plot(True)
        else:
            if self.yMin == 0 and self.yMax == 0:
                for p in self.plot:
                    p.set_axes_auto()
            else:
                for p in self.plot:
                    p.set_axes_semi_auto(self.yMin, self.yMax, 
                            Qwt.QwtPlot.yLeft, Qwt.QwtPlot.xBottom)
            p.get_zoomer().setZoomBase()
#                p.bottom_plot(True)

    def sync_axes(self, xMax, xMin):
        # Set axes to parameter values
        if (xMax > self.xMax):
            self.xMax = xMax
        if (xMin < self.xMin):
            self.xMin = xMin

    def set_y_limit(self, yMax, yMin):
        self.yMax = yMax
        self.yMin = yMin
        self.sync_toggled(self.parentWidget().sync_is_checked())

    def get_y_limit(self):
        self.emit(QtCore.SIGNAL("YUpdated"), self.yMax)

    def init_class_variables(self):
        self.plot = []
        self.xMax = 0
        self.xMin = 0

    def show_coordinates(self, position):
        # Emit a signal when a point on the plot has been clicked 
        self.emit(QtCore.SIGNAL("PositionChange"), position)

    def sync_zoom(self, rect):
        # Sync up the zooming of each plot
        for p in self.plot:
            p.get_zoomer().zoom(rect)
    
    def remove_plots(self):
        for p in self.plot:
            p.delete_plot()
            p.hide()
        self.plot = []

    def remove_means(self, toggled):
        for p in self.plot:
            if toggled:
                p.remove_mean()
            else:
                p.add_mean()

    def has_plots(self):
        if len(self.plot) > 0:
            return True
        else:
            return False

    def sizeHint(self):
        return QtCore.QSize(750, 500)

class PlotWidget(Qwt.QwtPlot):

    def __init__(self, data, widget_parent = None):
        # Init the base class
        Qwt.QwtPlot.__init__(self, widget_parent)

        # Init class variables
        self.curve = Qwt.QwtPlotCurve()
        self.curve.attach(self)
        self.x = []
        self.y = []
        self.polygon = QtGui.QPolygonF()
        self.bottomAxisVisible = False
        self.mean = self.get_mean(data)
        self.includesMean = True
        
        # Set background color and canvas margin
        self.setCanvasBackground(QtCore.Qt.white)
        self.plotLayout().setCanvasMargin(0)

        # Call initializer methods
        self.init_plot(data)
        self.init_picking()
        self.init_zooming()

        # Plot marker
        self.d_mrk1 = Qwt.QwtPlotMarker()
        self.d_mrk1.setLineStyle(Qwt.QwtPlotMarker.VLine)
        self.d_mrk1.setLabelAlignment(QtCore.Qt.AlignRight | 
                QtCore.Qt.AlignBottom)
        self.d_mrk1.attach(self)

    def init_picking(self):
        self.picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
                Qwt.QwtPlot.yLeft,
                Qwt.QwtPicker.PointSelection,
                Qwt.QwtPlotPicker.CrossRubberBand,
                Qwt.QwtPicker.AlwaysOn,
                self.canvas())

        QtCore.QObject.connect(self.picker,
                QtCore.SIGNAL("selected(const QwtDoublePoint&)"),
                self.parent().show_coordinates)

    def init_zooming(self):
        self.zoomer = Qwt.QwtPlotZoomer(Qwt.QwtPlot.xBottom,
                Qwt.QwtPlot.yRight,
                Qwt.QwtPicker.DragSelection,
                Qwt.QwtPicker.AlwaysOff,
                self.canvas())
        self.zoomer.setZoomBase()
        self.zoomer.zoomed.connect(self.parent().sync_zoom)

    def get_zoomer(self):
        return self.zoomer

    def init_plot(self, data):
        from scipy import signal
        #import time
        #start = time.clock()
        # Decimate data
        #data[0][:] = signal.decimate(data[0], 2)
        # Load x and y points from the data
        b = data[1]
        delta = data[2]


        # load x values
        self.x = [i * delta + delta for i in range(len(data[0]))]
        # shift x values by b
        self.x[:] = [i + b for i in self.x]
        # load y values
        self.y = [i for i in data[0]]

        #elapsed = time.clock() - start
        #print "MainWindow time: ", elapsed

    def get_mean(self, data):
        import math
        return math.fsum(data[0]) / len(data[0])

    def remove_mean(self):
        if self.includesMean:
            self.includesMean = False
            self.y[:] = [x - self.mean for x in self.y]
            self.curve.setData(self.x, self.y)
            self.replot()

    def add_mean(self):
        if not self.includesMean:
            self.includesMean = True
            self.y[:] = [x + self.mean for x in self.y]
            self.curve.setData(self.x, self.y)
            self.replot()

    def set_axes(self, xMax, xMin, yMax, yMin):
        # Set axes to particular numbers
        self.setAxisScale(Qwt.QwtPlot.xBottom, xMin, xMax)
        self.setAxisScale(Qwt.QwtPlot.yLeft, yMin, yMax)
        self.replot()

    def set_axes_semi_auto(self, minimum, maximum, axisIDman, axisIDauto):
        # Set only one axis from minimum to maximum and the other to auto
        self.setAxisScale(axisIDman, minimum, maximum)
        self.setAxisAutoScale(axisIDauto)
        self.replot()

    def set_axes_auto(self):
        # Let QwtPlot automatically create axes
        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        self.replot()

    def bottom_plot(self, bottom = False):
        self.bottomAxisVisible = bottom
        self.enableAxis(Qwt.QwtPlot.xBottom, bottom)
        self.replot()

    def delete_plot(self):
        self.curve.setData([], [])
        self.x = []
        self.y = []
        self.detachItems()

    def plot_label(self, plotName):
        label = QtGui.QLabel(plotName)

        text = Qwt.QwtText(plotName)

        self.d_mrk1.setLabel(text)

# Class for producing plots
class PlotWindow(QtGui.QMainWindow):

    def __init__(self, win_parent = None):
        import os

        # Init the base class
        QtGui.QMainWindow.__init__(self, win_parent)

        # Init class variables
        self.directoryPath = "" # temporary directory path
        self.startingPath = os.getcwd()
        self.ylim = SetYLimWidget()

        # Init the main window
        self.create_widgets()
        self.create_actions()
        self.create_toolbar()
        self.create_menus()
        self.create_connections()

        # Center window in the middle of the screen
        desktop = QtGui.QDesktopWidget()
        windowWidth = self.size().width()
        windowHeight = self.size().height()
        screenWidth = desktop.screenGeometry(desktop.primaryScreen()).width()
        screenHeight = desktop.screenGeometry(desktop.primaryScreen()).height()
        x = (screenWidth - windowWidth) / 2
        y = (screenHeight - windowHeight) / 2
        y = y - 50
        self.move(x, y)

    def create_widgets(self):
        # Set the central widget
        self.central_widget = CentralWidget(self)
        self.setCentralWidget(self.central_widget)

        # Add status bar to window
        statusbar = QtGui.QStatusBar()
        statusbar.setSizeGripEnabled(True)
        self.setStatusBar(statusbar)
        statusbar.showMessage(
                "Mouse movements in the plots are shown in the status bar")

        # Init menu bar 
        self.menubar = self.menuBar()

    def create_toolbar(self):
        # Add toolbar to QMainWindow
        toolbar = QtGui.QToolBar("ToolBar")
        
        # Create spacer widget to push addPlotAction to right of toolbar
        spacerWidget = QtGui.QWidget(self)
        spacerWidget.setSizePolicy(QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred))
        
        # Add widgets, actions, and set tool bar
        toolbar.addWidget(self.ylim)
        toolbar.addWidget(spacerWidget)
        toolbar.addAction(self.addPlotAction)
        toolbar.addAction(self.previousPlotAction)
        toolbar.addAction(self.nextPlotAction)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, toolbar)

    def create_actions(self):
        # Actions for the File Menu in the menu bar
        self.exitAction = QtGui.QAction("&Exit", self)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.setStatusTip("Exit application")
        self.exitAction.triggered.connect(self.close)

        self.importSeedAction = QtGui.QAction("&Import Seed File", self)
        self.importSeedAction.setShortcut("Ctrl+I")
        self.importSeedAction.setStatusTip("Import a SEED file")
        self.importSeedAction.triggered.connect(self.import_seed)

        # Actions for the Edit Menu
        self.syncAction = QtGui.QAction("S&ync", self)
        self.syncAction.setShortcut("Ctrl+Y")
        self.syncAction.setStatusTip("Check to sync the plots")
        self.syncAction.setCheckable(True)
        self.syncAction.setChecked(True)
        self.syncAction.toggled.connect(self.central_widget.sync_toggled)

        self.removeMeanAction = QtGui.QAction("Remove &Mean", self)
        self.removeMeanAction.setShortcut("Ctrl+M")
        self.removeMeanAction.setStatusTip("Remove Mean from Plots")
        self.removeMeanAction.setCheckable(True)
        self.removeMeanAction.setChecked(True)
        self.removeMeanAction.toggled.connect(
                self.central_widget.remove_means)

        self.addPlotAction = QtGui.QAction("&Add Plot", self)
        self.addPlotAction.setShortcut("Ctrl+A+P")
        self.addPlotAction.setStatusTip("Add a plot for viewing")
        self.addPlotAction.triggered.connect(self.central_widget.add_plot)

        self.nextPlotAction = QtGui.QAction("&Next Plot", self)
        self.nextPlotAction.setShortcut("Alt+N")
        self.nextPlotAction.setStatusTip("Show next set of plots")
        self.nextPlotAction.triggered.connect(self.next_clicked)

        self.previousPlotAction = QtGui.QAction("&Previous Plot", self)
        self.previousPlotAction.setShortcut("Alt+P")
        self.previousPlotAction.setStatusTip("Show previous set of plots")
        self.previousPlotAction.triggered.connect(self.previous_clicked)

    def create_menus(self):
        # File Menu
        self.fileMenu = self.menubar.addMenu("&File")
        self.fileMenu.addAction(self.importSeedAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        # Edit Menu
        self.editMenu = self.menubar.addMenu("&Edit")
        self.editMenu.addAction(self.addPlotAction)
        self.editMenu.addAction(self.syncAction)
        self.editMenu.addAction(self.removeMeanAction)

    def create_connections(self):
        QtCore.QObject.connect(self.central_widget,
                QtCore.SIGNAL("PositionChange"),
                self.show_coordinates)

        QtCore.QObject.connect(self.ylim,
                QtCore.SIGNAL("SetClicked"),
                self.set_clicked)

        QtCore.QObject.connect(self.ylim,
                QtCore.SIGNAL("YUpdated"),
                self.update_ylim)

    def update_ylim(self, yMax):
        self.ylim.set_line_value(xMax)

    def next_clicked(self):
        self.central_widget.remove_plots()
        self.central_widget.init_class_variables()
        self.increment_time()
        self.sac_driver()

    def previous_clicked(self):
        self.central_widget.remove_plots()
        self.central_widget.init_class_variables()
        self.decrement_time()
        self.sac_driver()

    def closeEvent(self, event):
        # Control what happens when the program is closed

        # Delete tmp file
        self.remove_temp_file()

        # Accept the close event to close the application
        event.accept()

    def update_ylim(self, yMax):
        # Update the value found in the ylim widget
        self.ylim.set_line_value(yMax)

    def set_clicked(self):
        # Slot for setting the y-limit
        yMax = self.ylim.get_line_value()
        self.central_widget.set_y_limit(yMax, (yMax * -1))

    # Return TRUE if syncAction is checked, FALSE otherwise
    def sync_is_checked(self):
        return self.syncAction.isChecked()

    def mean_is_checked(self):
        # Return TRUE if removeMeanAction is checked, FALSE otherwise
        return self.removeMeanAction.isChecked()

    def show_coordinates(self, position):
        # Display coordinates in the status bar of the position on the plot
        # where the user clicked
        self.statusBar().showMessage('x = ' + str(position.x())
                + ' y = ' + str(position.y()))

    def remove_temp_file(self):
        import shutil
        
        # If there was a tmp file created during the running
        # of this program, delete it.
        try:
            shutil.rmtree(self.directoryPath)
        except OSError, e:
            if e.errno != 2: # code 2 - no such file or directory
                raise

    def create_sac_files(self):
        import os

        starttime = self.get_time_rdseed_format( \
            self.startTime.toString("yyyyMMddhhmmss"))
        endtime = self.get_time_rdseed_format( \
            self.endTime.toString("yyyyMMddhhmmss"))
        collector = []
        for cb in self.checkboxInfo:
            for channel in cb[1]:
                if channel != "Null" and collector.count(channel) == 0:
                    collector.append(channel)

        channels = " ".join(collector)

        rdseed = 'echo \"' + self.seedName + \
                "\n\n\nd\n\n\n" + channels + "\n\n\n\n\n\n\n\n"\
                + starttime + "\n" + endtime + "\n\n\nQuit\n\"" \
                + '| rdseed'
        os.system(str(rdseed))

    def load_sac_files(self):
        import os

        sacFiles = []
        files = os.listdir(self.directoryPath)
        for cb in self.checkboxInfo:
            for channel in cb[1]:
                if channel != "Null":
                    for f in files:
                        if cb[0] in f and channel in f:
                            sacFiles.append(f)

        return sacFiles

    def increment_time(self):
        self.startTime = self.endTime
        self.endTime = self.endTime.addSecs(self.intervalTime)

    def decrement_time(self):
        self.endTime = self.startTime
        self.startTime = self.startTime.addSecs(-1 * self.intervalTime)

    def get_time_rdseed_format(self, fullTime):
        import julday 

        year = fullTime[:4] 
        month = fullTime[4:6] 
        day = fullTime[6:8] 
        hour = fullTime[8:10] 
        minute = fullTime[10:12] 
        second = fullTime[12:14] 
                                                 
        # Get julian day 
        julianDay = julday.calcday(int(year), int(month), int(day)) 
                                                                  
        # Return string containing rdseed date and time string 
        return str(year) + "," + str(julianDay) + "," + str(hour) + \
                ":" + str(minute) + ":" + str(second) + ".0000" 

    def import_seed(self):
        import seedinfodialog as sid
        # Read a seed file and get the information out of it

        # Slot that handles the importing of SEED files
        self.seedName = QtGui.QFileDialog.getOpenFileName(
                self, "Open SEED File", ".", "SEED Files (*.seed)")

        if self.seedName:
            # Reinitialize the central widget
            if self.central_widget.has_plots():
                self.central_widget.remove_plots()
                self.central_widget.init_class_variables()

            # If a SEED file was picked by the user, open up a dialog to
            # gather more information about what to display.
            seedInfo = sid.SeedInfoDialog(self.seedName, self)
            # Connect seedInfo dialog box with slot to do something
            QtCore.QObject.connect(seedInfo, 
                    QtCore.SIGNAL("ok_clicked"),
                    seedInfo.accept)
            QtCore.QObject.connect(seedInfo,
                    QtCore.SIGNAL("cancel_clicked"),
                    seedInfo.reject)
            dialogCode = seedInfo.exec_()
           
            if dialogCode == QtGui.QDialog.Accepted:
                self.startTime = seedInfo.get_start_time_info()
                self.endTime = seedInfo.get_end_time_info()
                self.intervalTime = seedInfo.get_interval_time()
                self.checkboxInfo = seedInfo.get_checkbox_info()
                self.sac_driver()
                    
    def sac_driver(self):
        import os
        # Remove old tmp directory
        if self.directoryPath != "":
            self.remove_temp_file()

        # Change directory to a temporary directory
        self.create_temp_folder()
        os.chdir(self.directoryPath)
        
        self.create_sac_files()
        for f in self.load_sac_files():
            self.central_widget.new_plot(f)

        # Remove mean from graphs if it is initially checked
        self.central_widget.remove_means(self.mean_is_checked())

        os.chdir(self.startingPath)

    def create_temp_folder(self):
        # Create a temporary folder for holding SAC files 
        import tempfile
        self.directoryPath = tempfile.mkdtemp()
