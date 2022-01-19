import qwt
from helpers.sacfilereader import sac_reader
from PyQt6.QtCore import QSize, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QGridLayout, QWidget

from widgets.plotwidget import PlotWidget


class CentralWidget(QWidget):
    # Create signals
    y_updated = pyqtSignal(int, name="YUpdated")
    position_change = pyqtSignal(int, name="position_change")

    def __init__(self, widget_parent=None):
        # Init the base class
        QWidget.__init__(self, widget_parent)

        # Define class variables
        self.init_class_variables()
        self.yMax = 0
        self.yMin = 0

        # Set the minimum size and layout
        self.setMinimumSize(750, 250)
        self.grid = QGridLayout()
        self.setLayout(self.grid)

    def get_file_info(self, filenames):
        data = sac_reader(filenames)
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
        self.sync_axes(round(data[1] + len(data[0]) * data[2]), data[1])

        # Call the function to sync or not based on user input
        self.sync_toggled(self.parentWidget().sync_is_checked())

    def add_plot(self):
        # Get a file from the user and add that file to the label of files
        fileName = QFileDialog.getOpenFileName(
            self, "Open SAC File", ".", "SAC Files (*.sac *.SAC *.*)"
        )
        if fileName:
            self.new_plot(fileName)

    def sync_toggled(self, checked):
        # What to do if sync is toggled on or off
        if checked:
            if self.yMin == 0 and self.yMax == 0:
                for p in self.plot:
                    p.set_axes_semi_auto(
                        self.xMin,
                        self.xMax,
                        qwt.QwtPlot.xBottom,
                        qwt.QwtPlot.yLeft,
                    )
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
                    p.set_axes_semi_auto(
                        self.yMin,
                        self.yMax,
                        qwt.QwtPlot.yLeft,
                        qwt.QwtPlot.xBottom,
                    )
            p.get_zoomer().setZoomBase()

    #                p.bottom_plot(True)

    def sync_axes(self, xMax, xMin):
        # Set axes to parameter values
        if xMax > self.xMax:
            self.xMax = xMax
        if xMin < self.xMin:
            self.xMin = xMin

    def set_y_limit(self, yMax, yMin):
        self.yMax = yMax
        self.yMin = yMin
        self.sync_toggled(self.parentWidget().sync_is_checked())

    def get_y_limit(self):
        self.y_updated.emit(self.yMax)

    def init_class_variables(self):
        self.plot = []
        self.xMax = 0
        self.xMin = 0

    @pyqtSlot()
    def show_coordinates(self, position):
        # Emit a signal when a point on the plot has been clicked
        self.position_change.emit(position)

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
        return QSize(750, 500)
