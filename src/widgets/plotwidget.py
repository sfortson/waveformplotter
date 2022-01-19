import math

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPolygonF


class PlotWidget(Qwt.QwtPlot):
    def __init__(self, data, widget_parent=None):
        # Init the base class
        Qwt.QwtPlot.__init__(self, widget_parent)

        # Init class variables
        self.curve = Qwt.QwtPlotCurve()
        self.curve.attach(self)
        self.x = []
        self.y = []
        self.polygon = QPolygonF()
        self.bottomAxisVisible = False
        self.mean = self.get_mean(data)
        self.includesMean = True

        # Set background color and canvas margin
        self.setCanvasBackground(Qt.GlobalColor.white)
        self.plotLayout().setCanvasMargin(0)

        # Call initializer methods
        self.init_plot(data)
        self.init_picking()
        self.init_zooming()

        # Plot marker
        self.d_mrk1 = Qwt.QwtPlotMarker()
        self.d_mrk1.setLineStyle(Qwt.QwtPlotMarker.VLine)
        self.d_mrk1.setLabelAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom
        )
        self.d_mrk1.attach(self)

    def init_picking(self):
        self.picker = Qwt.QwtPlotPicker(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.PointSelection,
            Qwt.QwtPlotPicker.CrossRubberBand,
            Qwt.QwtPicker.AlwaysOn,
            self.canvas(),
        )

        QtCore.QObject.connect(
            self.picker,
            QtCore.SIGNAL("selected(const QwtDoublePoint&)"),
            self.parent().show_coordinates,
        )

    def init_zooming(self):
        self.zoomer = Qwt.QwtPlotZoomer(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yRight,
            Qwt.QwtPicker.DragSelection,
            Qwt.QwtPicker.AlwaysOff,
            self.canvas(),
        )
        self.zoomer.setZoomBase()
        self.zoomer.zoomed.connect(self.parent().sync_zoom)

    def get_zoomer(self):
        return self.zoomer

    def init_plot(self, data):
        from scipy import signal

        # import time
        # start = time.clock()
        # Decimate data
        # data[0][:] = signal.decimate(data[0], 2)
        # Load x and y points from the data
        b = data[1]
        delta = data[2]

        # load x values
        self.x = [i * delta + delta for i in range(len(data[0]))]
        # shift x values by b
        self.x[:] = [i + b for i in self.x]
        # load y values
        self.y = [i for i in data[0]]

        # elapsed = time.clock() - start
        # print "MainWindow time: ", elapsed

    def get_mean(self, data):
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

    def bottom_plot(self, bottom=False):
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
