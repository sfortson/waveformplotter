import os
import shutil
import tempfile

from helpers.julday import calcday
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMainWindow,
    QSizePolicy,
    QStatusBar,
    QToolBar,
    QWidget,
)

from widgets.seedinfodialog import SeedInfoDialog
from widgets.ylimwidget import SetYLimWidget


# Class for producing plots
class PlotWindow(QMainWindow):
    def __init__(self, win_parent=None):
        # Init the base class
        QMainWindow.__init__(self, win_parent)

        # Init class variables
        self.directoryPath = ""  # temporary directory path
        self.startingPath = os.getcwd()
        self.ylim = SetYLimWidget()

        # Init the main window
        self.create_widgets()
        self.create_actions()
        self.create_toolbar()
        self.create_menus()
        self.create_connections()

    def create_widgets(self):
        # Set the central widget
        # self.central_widget = CentralWidget(self)
        # self.setCentralWidget(self.central_widget)

        # Add status bar to window
        statusbar = QStatusBar()
        statusbar.setSizeGripEnabled(True)
        self.setStatusBar(statusbar)
        statusbar.showMessage(
            "Mouse movements in the plots are shown in the status bar"
        )

        # Init menu bar
        self.menubar = self.menuBar()

    def create_toolbar(self):
        # Add toolbar to QMainWindow
        toolbar = QToolBar("ToolBar")

        # Create spacer widget to push addPlotAction to right of toolbar
        spacerWidget = QWidget(self)
        spacerWidget.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
        )

        # Add widgets, actions, and set tool bar
        toolbar.addWidget(self.ylim)
        toolbar.addWidget(spacerWidget)
        toolbar.addAction(self.addPlotAction)
        toolbar.addAction(self.previousPlotAction)
        toolbar.addAction(self.nextPlotAction)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, toolbar)

    def create_actions(self):
        # Actions for the File Menu in the menu bar
        self.exitAction = QAction("&Exit", self)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.setStatusTip("Exit application")
        self.exitAction.triggered.connect(self.close)

        self.importSeedAction = QAction("&Import Seed File", self)
        self.importSeedAction.setShortcut("Ctrl+I")
        self.importSeedAction.setStatusTip("Import a SEED file")
        self.importSeedAction.triggered.connect(self.import_seed)

        # Actions for the Edit Menu
        self.syncAction = QAction("S&ync", self)
        self.syncAction.setShortcut("Ctrl+Y")
        self.syncAction.setStatusTip("Check to sync the plots")
        self.syncAction.setCheckable(True)
        self.syncAction.setChecked(True)
        # self.syncAction.toggled.connect(self.central_widget.sync_toggled)

        self.removeMeanAction = QAction("Remove &Mean", self)
        self.removeMeanAction.setShortcut("Ctrl+M")
        self.removeMeanAction.setStatusTip("Remove Mean from Plots")
        self.removeMeanAction.setCheckable(True)
        self.removeMeanAction.setChecked(True)
        # self.removeMeanAction.toggled.connect(self.central_widget.remove_means)

        self.addPlotAction = QAction("&Add Plot", self)
        self.addPlotAction.setShortcut("Ctrl+A+P")
        self.addPlotAction.setStatusTip("Add a plot for viewing")
        # self.addPlotAction.triggered.connect(self.central_widget.add_plot)

        self.nextPlotAction = QAction("&Next Plot", self)
        self.nextPlotAction.setShortcut("Alt+N")
        self.nextPlotAction.setStatusTip("Show next set of plots")
        self.nextPlotAction.triggered.connect(self.next_clicked)

        self.previousPlotAction = QAction("&Previous Plot", self)
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
        # QtCore.QObject.connect(
        #     self.central_widget,
        #     QtCore.SIGNAL("PositionChange"),
        #     self.show_coordinates,
        # )

        self.ylim.set_clicked.connect(self.set_clicked)

    def next_clicked(self):
        # self.central_widget.remove_plots()
        # self.central_widget.init_class_variables()
        self.increment_time()
        self.sac_driver()

    def previous_clicked(self):
        # self.central_widget.remove_plots()
        # self.central_widget.init_class_variables()
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

    @pyqtSlot(int)
    def set_clicked(self, y_max):
        # Slot for setting the y-limit
        print(y_max)
        # self.central_widget.set_y_limit(y_max, (y_max * -1))

    # Return TRUE if syncAction is checked, FALSE otherwise
    def sync_is_checked(self):
        return self.syncAction.isChecked()

    def mean_is_checked(self):
        # Return TRUE if removeMeanAction is checked, FALSE otherwise
        return self.removeMeanAction.isChecked()

    def show_coordinates(self, position):
        # Display coordinates in the status bar of the position on the plot
        # where the user clicked
        self.statusBar().showMessage(
            "x = " + str(position.x()) + " y = " + str(position.y())
        )

    def remove_temp_file(self):
        # If there was a tmp file created during the running
        # of this program, delete it.
        try:
            shutil.rmtree(self.directoryPath)
        except OSError as e:
            if e.errno != 2:  # code 2 - no such file or directory
                raise

    def create_sac_files(self):
        starttime = self.get_time_rdseed_format(
            self.startTime.toString("yyyyMMddhhmmss")
        )
        endtime = self.get_time_rdseed_format(
            self.endTime.toString("yyyyMMddhhmmss")
        )
        collector = []
        for cb in self.checkboxInfo:
            for channel in cb[1]:
                if channel != "Null" and collector.count(channel) == 0:
                    collector.append(channel)

        channels = " ".join(collector)

        rdseed = (
            'echo "'
            + self.seedName
            + "\n\n\nd\n\n\n"
            + channels
            + "\n\n\n\n\n\n\n\n"
            + starttime
            + "\n"
            + endtime
            + '\n\n\nQuit\n"'
            + "| rdseed"
        )
        os.system(str(rdseed))

    def load_sac_files(self):
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

    @staticmethod
    def get_time_rdseed_format(fullTime):
        year = fullTime[:4]
        month = fullTime[4:6]
        day = fullTime[6:8]
        hour = fullTime[8:10]
        minute = fullTime[10:12]
        second = fullTime[12:14]

        # Get julian day
        julianDay = calcday(int(year), int(month), int(day))

        # Return string containing rdseed date and time string
        return (
            str(year)
            + ","
            + str(julianDay)
            + ","
            + str(hour)
            + ":"
            + str(minute)
            + ":"
            + str(second)
            + ".0000"
        )

    def import_seed(self):
        # Read a seed file and get the information out of it
        # Slot that handles the importing of SEED files
        self.seedName = QFileDialog.getOpenFileName(
            self, "Open SEED File", ".", "SEED Files (*.seed)"
        )

        if self.seedName and self.seedName != ("", ""):
            # Reinitialize the central widget
            # if self.central_widget.has_plots():
            #     self.central_widget.remove_plots()
            #     self.central_widget.init_class_variables()

            # If a SEED file was picked by the user, open up a dialog to
            # gather more information about what to display.
            seedInfo = SeedInfoDialog(self.seedName, self)
            # Connect seedInfo dialog box with slot to do something
            seedInfo.ok_clicked.connect(seedInfo.accept)
            seedInfo.cancel_clicked.connect(seedInfo.reject)
            dialogCode = seedInfo.exec()

            if dialogCode == QDialog.Accepted:
                self.startTime = seedInfo.get_start_time_info()
                self.endTime = seedInfo.get_end_time_info()
                self.intervalTime = seedInfo.get_interval_time()
                self.checkboxInfo = seedInfo.get_checkbox_info()
                self.sac_driver()

    def sac_driver(self):
        # Remove old tmp directory
        if self.directoryPath != "":
            self.remove_temp_file()

        # Change directory to a temporary directory
        self.create_temp_folder()
        os.chdir(self.directoryPath)

        self.create_sac_files()
        # for f in self.load_sac_files():
        #     self.central_widget.new_plot(f)

        # Remove mean from graphs if it is initially checked
        # self.central_widget.remove_means(self.mean_is_checked())

        os.chdir(self.startingPath)

    def create_temp_folder(self):
        # Create a temporary folder for holding SAC files
        self.directoryPath = tempfile.mkdtemp()
