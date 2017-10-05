#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
import PyQt4.Qwt5 as Qwt

class TimeSelector(QtGui.QGroupBox):

    def __init__(self, startTime, endTime, parent):
        # Init the base class
        QtGui.QGroupBox.__init__(self, "Select Start and End Times", parent)

        # Define class variables
        self.startDateTime = QtGui.QDateTimeEdit(self)
        self.endDateTime = QtGui.QDateTimeEdit(self)
        self.init_dates_and_times(startTime, endTime)
        
        # Init the widgets
        self.init_widgets(startTime, endTime)

    def init_dates_and_times(self, startTime, endTime):
        import julday
        # Get the start time of the seed file
        stmp = startTime.split(",")
        syear = str(stmp[0])
        sjulianDay = str(stmp[1])
        sfullTime = str(stmp[2])
        shour = sfullTime.split(":")[0]
        sminute = sfullTime.split(":")[1]
        ssecond = float(sfullTime.split(":")[2])
        scalday = julday.dayofyear(int(syear), int(sjulianDay))
        smonth = scalday[:2]
        sday = scalday[2:4]

        # Get the end time of the seed file
        etmp = endTime.split(",")
        eyear = str(etmp[0])
        ejulianDay = str(etmp[1])
        efullTime = str(etmp[2])
        ehour = efullTime.split(":")[0]
        eminute = efullTime.split(":")[1]
        esecond = float(efullTime.split(":")[2])
        ecalday = julday.dayofyear(int(eyear), int(ejulianDay))
        emonth = ecalday[:2]
        eday = ecalday[2:4]

        # Set min and max dates for QDateTimeEdits
        self.minDate = QtCore.QDate(int(syear), int(smonth), int(sday))
        self.maxDate = QtCore.QDate(int(eyear), int(emonth), int(eday))

        # Set min and max times for QDateTimeEdits
        self.minTime = \
                QtCore.QTime(int(shour), int(sminute), int(round(ssecond)))
        self.maxTime = \
                QtCore.QTime(int(ehour), int(eminute), int(round(esecond)))
        
        # Set min and max QDateTimes for QDateTimeEdits
        self.minimumDateTime = QtCore.QDateTime(self.minDate,
                QtCore.QTime(int(shour), int(sminute), int(round(ssecond))))
        self.maximumDateTime = QtCore.QDateTime(self.maxDate,
                QtCore.QTime(int(ehour), int(eminute), int(round(esecond))))

    def init_widgets(self, startTime, endTime):
        self.startDateTime.setMinimumDate(self.minDate)
        self.startDateTime.setMaximumDate(self.maxDate)
        self.startDateTime.setDateTime(self.minimumDateTime)
        self.endDateTime.setMinimumDate(self.minDate)
        self.endDateTime.setMaximumDate(self.maxDate)
        self.endDateTime.setDateTime(self.minimumDateTime)

        # Set Layout
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel("Start Time:"), 0, 0)
        layout.addWidget(self.startDateTime, 0, 1)
        layout.addWidget(QtGui.QLabel("End Time:"), 1, 0)
        layout.addWidget(self.endDateTime, 1, 1)
        self.setLayout(layout)

    def get_start_datetime(self):
        if self.startDateTime.dateTime() >= self.minimumDateTime:
            return self.startDateTime.dateTime()
        else:
            return self.minimumDateTime

    def get_end_datetime(self):
        if self.endDateTime.dateTime() <= self.maximumDateTime:
            return self.endDateTime.dateTime()
        else:
            return self.maximumDateTime

    def get_interval_time(self):
        return self.get_start_datetime() \
                .secsTo(self.get_end_datetime())

class StationCheckBox(QtGui.QWidget):

    def __init__(self, sta, cha1, cha2, chaz, parent):
        # Init the base class
        QtGui.QWidget.__init__(self, parent)

        # Create checkboxes
        self.staBox = QtGui.QCheckBox(QtCore.QString(sta))
        self.chaOneBox = QtGui.QCheckBox(QtCore.QString(cha1))
        self.chaTwoBox = QtGui.QCheckBox(QtCore.QString(cha2))
        self.chaZBox = QtGui.QCheckBox(QtCore.QString(chaz))

        self.create_checkboxes()

    def create_checkboxes(self):
        # Create layout for checkboxes
        h_box = QtGui.QHBoxLayout(self)
        # Add Checkboxes to layout
        h_box.addWidget(self.staBox)
        h_box.addWidget(self.chaOneBox)
        h_box.addWidget(self.chaTwoBox)
        h_box.addWidget(self.chaZBox)
        # Set this widget's layout and groupbox
        self.setLayout(h_box)

        # Connect boxes with slots and set station box to be a tristate
        self.staBox.stateChanged.connect(self.sta_box_checked)
        self.chaOneBox.stateChanged.connect(self.channel_box_checked)
        self.chaTwoBox.stateChanged.connect(self.channel_box_checked)
        self.chaZBox.stateChanged.connect(self.channel_box_checked)

        # Set the channel Z checkbox to true (this is the default behavior)
        self.chaZBox.setCheckState(QtCore.Qt.Checked)

    def sta_box_checked(self, state):
        # Set the behavior of the station check box when 
        # its state changes
        if state == QtCore.Qt.Checked:
            self.check_all()
        elif state == QtCore.Qt.Unchecked:
            self.uncheck_all()

    def channel_box_checked(self, state):
        if state == QtCore.Qt.Checked:
            self.staBox.setCheckState(QtCore.Qt.PartiallyChecked)
            if self.all_boxes_checked():
                self.staBox.setCheckState(QtCore.Qt.Checked)
        if state == QtCore.Qt.Unchecked:
            self.staBox.setCheckState(QtCore.Qt.PartiallyChecked)
            if self.all_boxes_unchecked():
                self.staBox.setCheckState(QtCore.Qt.Unchecked)

    def check_all(self):
        # Check all of the channel boxes
        self.chaOneBox.setCheckState(QtCore.Qt.Checked)
        self.chaTwoBox.setCheckState(QtCore.Qt.Checked)
        self.chaZBox.setCheckState(QtCore.Qt.Checked)

    def uncheck_all(self):
        # Uncheck all of the channel boxes
        self.chaOneBox.setCheckState(QtCore.Qt.Unchecked)
        self.chaTwoBox.setCheckState(QtCore.Qt.Unchecked)
        self.chaZBox.setCheckState(QtCore.Qt.Unchecked)

    def all_boxes_checked(self):
        # Return TRUE if all channel boxes are checked, FALSE otherwise
        return (self.chaOneBox.checkState() == 
                self.chaTwoBox.checkState() ==
                self.chaZBox.checkState() == QtCore.Qt.Checked)
    
    def all_boxes_unchecked(self):
        # Return TRUE if all channel boxes are checked, FALSE otherwise
        return (self.chaOneBox.checkState() == 
                self.chaTwoBox.checkState() ==
                self.chaZBox.checkState() == QtCore.Qt.Unchecked)

    def get_checked_channels(self):
        # Return the channels checked by the user in list format
        stationInfo = []

        # Init channelsChecked
        channelsChecked = ["Null", "Null", "Null"]
        
        station = str(self.staBox.text())
        channelOne = str(self.chaOneBox.text())
        channelTwo = str(self.chaTwoBox.text())
        channelZ = str(self.chaZBox.text())

        stationInfo.append(station)
        if self.chaOneBox.isChecked() : channelsChecked[0] = channelOne 
        if self.chaTwoBox.isChecked() : channelsChecked[1] = channelTwo
        if self.chaZBox.isChecked()   : channelsChecked[2] = channelZ
        
        stationInfo.append(channelsChecked)

        return stationInfo

class SeedInfoDialog(QtGui.QDialog):

    def __init__(self, seedName, dialog_parent = None):
        # Init the base class
        QtGui.QDialog.__init__(self, dialog_parent)

        # Init class variables
        self.buttonBox = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Ok |
                QtGui.QDialogButtonBox.Cancel)

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
        self.emit(QtCore.SIGNAL("ok_clicked"))

    def cancel_clicked(self):
        # Emit a signale when the cancel button is clicked
        self.emit(QtCore.SIGNAL("cancel_clicked"))

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
        import os

        sacFiles = []
        seedName = self.get_seed_name()
        starttime = self.get_start_time_info()
        endtime = self.get_end_time_info()
        rdseed = 'echo \"' + seedName + \
                "\n\n\nd\n\n\n\n\n\n\n\n\n\n\n"\
                + starttime + "\n" + endtime + "\n\n\nQuit\n\"" \
                + '| rdseed'
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
        grid_layout = QtGui.QGridLayout()
        row = 0

        # Add TimeSelector widget to dialog 
        self.timeSelector = TimeSelector(self.stationInfo[0][3],
                self.stationInfo[0][6], self)
        grid_layout.addWidget(self.timeSelector, row, 0)
        row = row + 1

        # Add StationCheckBox widget to dialog
        # Add these widgets to a groupbox
        group_box = QtGui.QGroupBox("Select Stations and Channels", self)
        gb_layout = QtGui.QVBoxLayout()

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
        import os
        import tempfile
        
        # Set rdseed output file name
        f = tempfile.NamedTemporaryFile('rw')

        # Make the command that is used to call rdseed
        command = "rdseed -c -f " + seedName + " > " + f.name
        os.system(str(command))

        # Remove rdseed error file
        for log in os.listdir(os.getcwd()):
            if "rdseed.err_log" in log:
                os.remove(log)

        # Open up the file created by rdseed and gather necessary information
        #f = open(infoFileName, 'r')
        i = iter(f.readlines())
        data = []
        data2 = []
        while True:
            try:
                line = i.next()
                if not line.startswith('#'):
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
