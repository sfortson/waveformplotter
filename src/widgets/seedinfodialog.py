import os
import tempfile

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QVBoxLayout,
)

from widgets.stationcheckbox import StationCheckBox
from widgets.timeselector import TimeSelector


class SeedInfoDialog(QDialog):
    # Create signals
    ok_clicked = pyqtSignal(name="ok_clicked")
    cancel_clicked = pyqtSignal(name="cancel_clicked")

    def __init__(self, seedName, dialog_parent=None):
        # Init the base class
        QDialog.__init__(self, dialog_parent)

        # Init class variables
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        # List containing station info read from rdseed, and a list of
        # StationCheckBox objects
        self.stationInfo = []
        self.stationCheckBoxes = []
        self.seedName = seedName

        # Call function to retrieve SEED file header information
        self.get_seed_info(self.seedName)

        # Call functions to create and display dialog box
        self.create_widgets()

        # Connect Dialog SIGNALS and SLOTS
        self.create_connections()

    def create_connections(self):
        # Create the connections for the OK and CANCEL buttons
        self.buttonBox.accepted.connect(self.ok_clicked)
        self.buttonBox.rejected.connect(self.cancel_clicked)

    def ok_clicked(self):
        # Emit a signal when the ok button is clicked
        self.ok_clicked.emit()

    def cancel_clicked(self):
        # Emit a signale when the cancel button is clicked
        self.cancel_clicked.emit()

    def get_start_time_info(self):
        # Return the starting time and date info
        return self.timeSelector.get_start_datetime()

    def get_end_time_info(self):
        # Return the starting time and date info
        return self.timeSelector.get_end_datetime()

    def get_interval_time(self):
        # Return the interval, in seconds, between the start and end times
        return self.timeSelector.get_interval_time()

    def get_checkbox_info(self):
        checkBoxInfo = []
        for s in self.stationCheckBoxes:
            checkBoxInfo.append(s.get_checked_channels())
        return checkBoxInfo

    def get_sac_files(self, directory):
        sacFiles = []
        seedName = self.get_seed_name()
        starttime = self.get_start_time_info()
        endtime = self.get_end_time_info()
        rdseed = (
            'echo "'
            + seedName
            + "\n\n\nd\n\n\n\n\n\n\n\n\n\n\n"
            + starttime
            + "\n"
            + endtime
            + '\n\n\nQuit\n"'
            + "| rdseed"
        )
        os.system(str(rdseed))
        files = os.listdir(directory)
        for cb in self.get_checkbox_info():
            for channel in cb[1]:
                if channel != "Null":
                    for f in files:
                        if cb[0] in f and channel in f:
                            sacFiles.append(f)

        return sacFiles

    def get_seed_name(self):
        return self.seedName

    def create_widgets(self):
        # Create the grid layout
        grid_layout = QGridLayout()
        row = 0

        # Add TimeSelector widget to dialog
        self.timeSelector = TimeSelector(
            self.stationInfo[0][3], self.stationInfo[0][6], self
        )
        grid_layout.addWidget(self.timeSelector, row, 0)
        row = row + 1

        # Add StationCheckBox widget to dialog
        # Add these widgets to a groupbox
        group_box = QGroupBox("Select Stations and Channels", self)
        gb_layout = QVBoxLayout()

        for s in self.stationInfo:
            sta = StationCheckBox(s[0], s[1], s[8], s[15], self)
            self.stationCheckBoxes.append(sta)
            gb_layout.addWidget(sta)
            row = row + 1

        group_box.setLayout(gb_layout)
        grid_layout.addWidget(group_box)

        # Add OK and CANCEL buttons to the dialog
        grid_layout.addWidget(self.buttonBox, row, 0)

        # Set this dialog's layout to the grid layout
        self.setLayout(grid_layout)

    def get_seed_info(self, seedName):
        # Set rdseed output file name
        f = tempfile.NamedTemporaryFile("rw")

        # Make the command that is used to call rdseed
        command = "rdseed -c -f " + seedName + " > " + f.name
        os.system(str(command))

        # Remove rdseed error file
        for log in os.listdir(os.getcwd()):
            if "rdseed.err_log" in log:
                os.remove(log)

        # Open up the file created by rdseed and gather necessary information
        # f = open(infoFileName, 'r')
        i = iter(f.readlines())
        data = []
        data2 = []
        while True:
            try:
                line = i.next()
                if not line.startswith("#"):
                    data.append(line)
            except StopIteration:
                break

        for d in data:
            if len(d) == 105:
                data2.append(d.strip().split())

        self.reorganize_station_info(data2)
        f.close()

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
                self.stationInfo.append(station)
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
        self.stationInfo.append(station)
