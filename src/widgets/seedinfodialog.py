"""Dialog box for display information read from SEED file."""

import os
import tempfile
from typing import List

from PyQt6.QtCore import QDateTime, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QVBoxLayout,
)

from helpers.sacfilereader import rdseed_name
from widgets.stationcheckbox import StationCheckBox
from widgets.timeselector import TimeSelector


class SeedInfoDialog(QDialog):
    """Dialog box for displaying information about the SEED file to the user

    :param seedName: Name of the SEED file
    :type seedName: str
    :param dialog_parent: Parent widget, defaults to None
    :type dialog_parent: QWidget, optional
    """

    # Create signals
    ok_clicked = pyqtSignal(name="ok_clicked")
    cancel_clicked = pyqtSignal(name="cancel_clicked")

    def __init__(self, seedName: str, dialog_parent=None):
        # Init the base class
        QDialog.__init__(self, dialog_parent)

        # Init class variables
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        # List containing station info read from rdseed, and a list of
        # StationCheckBox objects
        self.station_info = []
        self.station_check_boxes = []
        self.seed_name = seedName

        # Call function to retrieve SEED file header information
        self.get_seed_info(self.seed_name)

        # Call functions to create and display dialog box
        self._create_widgets()

        # Connect Dialog SIGNALS and SLOTS
        self._create_connections()

    def _create_connections(self) -> None:
        # Create the connections for the OK and CANCEL buttons
        self.button_box.accepted.connect(self.ok_clicked)
        self.button_box.rejected.connect(self.cancel_clicked)

    @pyqtSlot()
    def ok_button_clicked(self) -> None:
        """Emit a signal when the ok button is clicked"""
        self.ok_clicked.emit()

    @pyqtSlot()
    def cancel_button_clicked(self) -> None:
        """Emit a signale when the cancel button is clicked"""
        self.cancel_clicked.emit()

    def get_start_time_info(self) -> QDateTime:
        """Return the starting time and date info

        :return: Starting data and time info
        :rtype: QDateTime
        """
        return self.time_selector.get_start_datetime()

    def get_end_time_info(self) -> QDateTime:
        """Return the starting time and date info

        :return: starting time and date info
        :rtype: QDateTime
        """
        return self.time_selector.get_end_datetime()

    def get_interval_time(self) -> int:
        """Return the interval, in seconds, between the start and end times

        :return: interval, in seconds, between the start and end times
        :rtype: int
        """
        #
        return self.time_selector.get_interval_time()

    def get_checkbox_info(self) -> List[List[str]]:
        """Get all channel checkbox state

        :return: List of lists containing channel checkbox state
        :rtype: List[List[str]]
        """
        check_box_info = []
        for station in self.station_check_boxes:
            check_box_info.append(station.get_checked_channels())
        return check_box_info

    def get_sac_files(self, directory: str) -> List[str]:
        """Get SAC files corresponding to selected channels

        :param directory: Directory where to look for SAC files
        :type directory: str
        :return: List of SAC files
        :rtype: List[str]
        """
        sac_files = []
        seed_name = self.get_seed_name()
        start_time = self.get_start_time_info()
        end_time = self.get_end_time_info()
        rdseed = rdseed_name(seed_name, start_time, end_time)
        os.system(str(rdseed))
        files = os.listdir(directory)
        for checkbox in self.get_checkbox_info():
            for channel in checkbox[1]:
                if channel != "Null":
                    for sac_file in files:
                        if checkbox[0] in sac_file and channel in sac_file:
                            sac_files.append(sac_file)

        return sac_files

    def get_seed_name(self) -> str:
        """Get SEED file name

        :return: SEED file name
        :rtype: str
        """
        return self.seed_name

    def _create_widgets(self) -> None:
        # Create the grid layout
        grid_layout = QGridLayout()
        row = 0

        # Add TimeSelector widget to dialog
        self.time_selector = TimeSelector(
            self.station_info[0][3], self.station_info[0][6], self
        )
        grid_layout.addWidget(self.time_selector, row, 0)
        row = row + 1

        # Add StationCheckBox widget to dialog
        # Add these widgets to a groupbox
        group_box = QGroupBox("Select Stations and Channels", self)
        gb_layout = QVBoxLayout()

        for station in self.station_info:
            sta = StationCheckBox(station[0], station[1], station[8], station[15], self)
            self.station_check_boxes.append(sta)
            gb_layout.addWidget(sta)
            row = row + 1

        group_box.setLayout(gb_layout)
        grid_layout.addWidget(group_box)

        # Add OK and CANCEL buttons to the dialog
        grid_layout.addWidget(self.button_box, row, 0)

        # Set this dialog's layout to the grid layout
        self.setLayout(grid_layout)

    def get_seed_info(self, seed_name: str) -> None:
        """[summary]

        :param seed_name: [description]
        :type seed_name: str
        """
        # Set rdseed output file name
        with tempfile.NamedTemporaryFile("rw") as temp_file:

            # Make the command that is used to call rdseed
            command = "rdseed -c -f " + seed_name + " > " + temp_file.name
            os.system(str(command))

            # Remove rdseed error file
            for log in os.listdir(os.getcwd()):
                if "rdseed.err_log" in log:
                    os.remove(log)

            # Open up the file created by rdseed and gather necessary information
            # f = open(infoFileName, 'r')
            i = iter(temp_file.readlines())
            data = []
            data2 = []
            while True:
                try:
                    line = i.next()
                    if not line.startswith("#"):
                        data.append(line)
                except StopIteration:
                    break

            for datum in data:
                if len(datum) == 105:
                    data2.append(datum.strip().split())

            self.reorganize_station_info(data2)

    def reorganize_station_info(self, data):
        # --- Future work: Create an object instead of list? ---

        # Reorganizes the stationInfo list into the following format:
        # sta, cha, net, loc, start time, end time, sample rate, tot samples,
        # cha, net, loc, start time, end time, sample rate, tot samples,
        # cha, net, loc, start time, end time, sample rate, tot samples,
        station = []
        staName = str(data[0][1])
        station.append(staName)
        for d in data:
            if staName != str(d[1]):
                self.station_info.append(station)
                station = []
                staName = str(d[1])
                station.append(staName)

            if "LOG" not in d[2]:
                if station.count(d[2]) != 0:
                    station[3] = sorted([station[3], d[4]])[0]
                    station[6] = sorted([station[6], d[7]])[-1]
                else:
                    station.append(str(d[2]))
                    station.append(str(d[3]))
                    station.append(str(d[4]))
                    station.append(str(d[5]))
                    station.append(str(d[6]))
                    station.append(str(d[7]))
                    station.append(str(d[8]))
        self.station_info.append(station)
