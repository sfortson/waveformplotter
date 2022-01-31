"""Main window for Waveform Plotter."""

import os
import shutil
import tempfile
from typing import List

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

from helpers.julday import calcday
from helpers.sacfilereader import rdseed_name
from widgets.centralwidget import CentralWidget
from widgets.seedinfodialog import SeedInfoDialog
from widgets.ylimwidget import SetYLimWidget


def remove_temp_file(path):
    """If there was a tmp file created during the running of this program, delete it."""
    try:
        shutil.rmtree(path)
    except OSError as err:
        if err.errno != 2:  # code 2 - no such file or directory
            raise


def get_time_rdseed_format(full_time) -> str:
    """
    Get the time in rseed format.

    @return str
    """
    year = full_time[:4]
    month = full_time[4:6]
    day = full_time[6:8]
    hour = full_time[8:10]
    minute = full_time[10:12]
    second = full_time[12:14]

    # Get julian day
    julian_day = calcday(int(year), int(month), int(day))

    # Return string containing rdseed date and time string
    return (
        str(year)
        + ","
        + str(julian_day)
        + ","
        + str(hour)
        + ":"
        + str(minute)
        + ":"
        + str(second)
        + ".0000"
    )


# Class for producing plots
class PlotWindow(QMainWindow):
    """QMainWindow for Waveform Plotter."""

    def __init__(self, win_parent=None):
        # Init the base class
        QMainWindow.__init__(self, win_parent)

        # Init class variables
        self.directory_path = ""  # temporary directory path
        self.ylim = SetYLimWidget()
        self.start_time = None
        self.end_time = None
        self.interval_time = None
        self.checkbox_info = None
        self.seed_name = None

        # Init the main window
        self._create_menu_bar()
        self._create_widgets()
        self._create_toolbar()
        self._create_connections()

    def _create_widgets(self) -> None:
        """Create Widgets."""

        # Set the central widget
        self.central_widget = CentralWidget(self)
        self.setCentralWidget(self.central_widget)

        # Add status bar to window
        statusbar = QStatusBar()
        statusbar.setSizeGripEnabled(True)
        self.setStatusBar(statusbar)
        statusbar.showMessage(
            "Mouse movements in the plots are shown in the status bar"
        )

    def _create_toolbar(self) -> None:
        next_plot_action = QAction("&Next Plot", self)
        next_plot_action.setShortcut("Alt+N")
        next_plot_action.setStatusTip("Show next set of plots")
        next_plot_action.triggered.connect(self.next_clicked)

        previous_plot_action = QAction("&Previous Plot", self)
        previous_plot_action.setShortcut("Alt+P")
        previous_plot_action.setStatusTip("Show previous set of plots")
        previous_plot_action.triggered.connect(self.previous_clicked)
        # Add toolbar to QMainWindow
        toolbar = QToolBar("ToolBar")

        # Create spacer widget to push addPlotAction to right of toolbar
        spacer_widget = QWidget(self)
        spacer_widget.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        )

        # Add widgets, actions, and set tool bar
        toolbar.addWidget(self.ylim)
        toolbar.addWidget(spacer_widget)
        toolbar.addAction(self.add_plot_action)
        toolbar.addAction(previous_plot_action)
        toolbar.addAction(next_plot_action)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, toolbar)

    def _create_menu_bar(self) -> None:
        """Create edit menu and associated actions."""
        # Init menu bar
        menubar = self.menuBar()

        # Actions for the Edit Menu
        sync_action = QAction("S&ync", self)
        sync_action.setShortcut("Ctrl+Y")
        sync_action.setStatusTip("Check to sync the plots")
        sync_action.setCheckable(True)
        sync_action.setChecked(True)
        # self.syncAction.toggled.connect(self.central_widget.sync_toggled)

        remove_mean_action = QAction("Remove &Mean", self)
        remove_mean_action.setShortcut("Ctrl+M")
        remove_mean_action.setStatusTip("Remove Mean from Plots")
        remove_mean_action.setCheckable(True)
        remove_mean_action.setChecked(True)
        # self.removeMeanAction.toggled.connect(self.central_widget.remove_means)

        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)

        import_seed_action = QAction("&Import Seed File", self)
        import_seed_action.setShortcut("Ctrl+I")
        import_seed_action.setStatusTip("Import a SEED file")
        import_seed_action.triggered.connect(self.import_seed)

        # File Menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(import_seed_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.add_plot_action)
        edit_menu.addAction(sync_action)
        edit_menu.addAction(remove_mean_action)

    @property
    def add_plot_action(self) -> QAction:
        """Action for the action that adds plots to the main window."""

        action = QAction("&Add Plot", self)
        action.setShortcut("Ctrl+A+P")
        action.setStatusTip("Add a plot for viewing")
        # self.addPlotAction.triggered.connect(self.central_widget.add_plot)
        return action

    def _create_connections(self) -> None:
        # QtCore.QObject.connect(
        #     self.central_widget,
        #     QtCore.SIGNAL("PositionChange"),
        #     self.show_coordinates,
        # )

        self.ylim.set_clicked.connect(self.set_clicked)

    @pyqtSlot()
    def next_clicked(self) -> None:
        """Slot to handle next clicked button."""
        # self.central_widget.remove_plots()
        # self.central_widget.init_class_variables()
        self.increment_time()
        self.sac_driver()

    @pyqtSlot()
    def previous_clicked(self) -> None:
        """Slot to handle previous clicked button."""
        # self.central_widget.remove_plots()
        # self.central_widget.init_class_variables()
        self.decrement_time()
        self.sac_driver()

    def closeEvent(self, event) -> None:
        """Control what happens when the program is closed."""
        # pylint: disable=invalid-name

        # Delete tmp file
        remove_temp_file(self.directory_path)

        # Accept the close event to close the application
        event.accept()

    @pyqtSlot()
    def update_ylim(self, y_max) -> None:
        """Update the value found in the ylim widget."""
        self.ylim.set_line_value(y_max)

    @pyqtSlot(int)
    def set_clicked(self, y_max) -> None:
        """Slot for setting the y-limit."""
        # pylint: disable=no-self-use
        print(y_max)
        # self.central_widget.set_y_limit(y_max, (y_max * -1))

    def sync_is_checked(self) -> bool:
        """
        Return TRUE if syncAction is checked, FALSE otherwise.

        @return bool
        """
        return self.sync_action.isChecked()

    def mean_is_checked(self) -> bool:
        """
        Return TRUE if removeMeanAction is checked, FALSE otherwise.

        @return bool
        """
        return self.remove_mean_action.isChecked()

    @pyqtSlot()
    def show_coordinates(self, position) -> None:
        """Display coordinates in the status bar of the position on the
        plot where the user clicked."""
        self.statusBar().showMessage(
            "x = " + str(position.x()) + " y = " + str(position.y())
        )

    def create_sac_files(self) -> None:
        """Create SAC files."""
        starttime = self.get_time_rdseed_format(
            self.start_time.toString("yyyyMMddhhmmss")
        )
        endtime = self.get_time_rdseed_format(self.end_time.toString("yyyyMMddhhmmss"))
        collector = []
        for info in self.checkbox_info:
            for channel in info[1]:
                if channel != "Null" and collector.count(channel) == 0:
                    collector.append(channel)

        channels = " ".join(collector)

        rdseed = rdseed_name(self.seed_name, starttime, endtime, channels=channels)

        os.system(str(rdseed))

    def load_sac_files(self) -> List[str]:
        """
        Return list of sac file names.

        @return List[str]
        """
        sac_files = []
        files = os.listdir(self.directory_path)
        for info in self.checkbox_info:
            for channel in info[1]:
                if channel != "Null":
                    for file in files:
                        if info[0] in file and channel in file:
                            sac_files.append(file)

        return sac_files

    def increment_time(self) -> None:
        """Increment the time."""
        self.start_time = self.end_time
        self.end_time = self.end_time.addSecs(self.interval_time)

    def decrement_time(self) -> None:
        """Decrement the time."""
        self.end_time = self.start_time
        self.start_time = self.start_time.addSecs(-1 * self.interval_time)

    @pyqtSlot()
    def import_seed(self) -> None:
        """Read a seed file and get the information out of it.
        This is a slot that handles the importing of SEED files"""

        self.seed_name = QFileDialog.getOpenFileName(
            self, "Open SEED File", ".", "SEED Files (*.seed)"
        )

        if self.seed_name and self.seed_name != ("", ""):
            # Reinitialize the central widget
            # if self.central_widget.has_plots():
            #     self.central_widget.remove_plots()
            #     self.central_widget.init_class_variables()

            # If a SEED file was picked by the user, open up a dialog to
            # gather more information about what to display.
            seed_info = SeedInfoDialog(self.seed_name, self)
            # Connect seedInfo dialog box with slot to do something
            seed_info.ok_clicked.connect(seed_info.accept)
            seed_info.cancel_clicked.connect(seed_info.reject)
            dialog_code = seed_info.exec()

            if dialog_code == QDialog.Accepted:
                self.start_time = seed_info.get_start_time_info()
                self.end_time = seed_info.get_end_time_info()
                self.interval_time = seed_info.get_interval_time()
                self.checkbox_info = seed_info.get_checkbox_info()
                self.sac_driver()

    def sac_driver(self) -> None:
        """Create tmp folder and sac files."""
        # Remove old tmp directory
        if self.directory_path != "":
            remove_temp_file(self.directory_path)

        # Change directory to a temporary directory
        self.create_temp_folder()
        os.chdir(self.directory_path)

        self.create_sac_files()
        # for f in self.load_sac_files():
        #     self.central_widget.new_plot(f)

        # Remove mean from graphs if it is initially checked
        # self.central_widget.remove_means(self.mean_is_checked())

        os.chdir(os.getcwd())

    def create_temp_folder(self) -> None:
        """Create a temporary folder for holding SAC files."""
        self.directory_path = tempfile.mkdtemp()
