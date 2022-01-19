from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QWidget


class StationCheckBox(QWidget):
    def __init__(self, sta, cha1, cha2, chaz, parent):
        # Init the base class
        QWidget.__init__(self, parent)

        # Create checkboxes
        self.staBox = QCheckBox(str(sta))
        self.chaOneBox = QCheckBox(str(cha1))
        self.chaTwoBox = QCheckBox(str(cha2))
        self.chaZBox = QCheckBox(str(chaz))

        self.create_checkboxes()

    def create_checkboxes(self):
        # Create layout for checkboxes
        h_box = QHBoxLayout(self)
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
        self.chaZBox.setCheckState(Qt.CheckState.Checked)

    def sta_box_checked(self, state):
        # Set the behavior of the station check box when
        # its state changes
        if state == Qt.CheckState.Checked:
            self.check_all()
        elif state == Qt.CheckState.Unchecked:
            self.uncheck_all()

    def channel_box_checked(self, state):
        if state == Qt.CheckState.Checked:
            self.staBox.setCheckState(Qt.CheckState.PartiallyChecked)
            if self.all_boxes_checked():
                self.staBox.setCheckState(Qt.CheckState.Checked)
        if state == Qt.CheckState.Unchecked:
            self.staBox.setCheckState(Qt.CheckState.PartiallyChecked)
            if self.all_boxes_unchecked():
                self.staBox.setCheckState(Qt.CheckState.Unchecked)

    def check_all(self):
        # Check all of the channel boxes
        self.chaOneBox.setCheckState(Qt.CheckState.Checked)
        self.chaTwoBox.setCheckState(Qt.CheckState.Checked)
        self.chaZBox.setCheckState(Qt.CheckState.Checked)

    def uncheck_all(self):
        # Uncheck all of the channel boxes
        self.chaOneBox.setCheckState(Qt.CheckState.Unchecked)
        self.chaTwoBox.setCheckState(Qt.CheckState.Unchecked)
        self.chaZBox.setCheckState(Qt.CheckState.Unchecked)

    def all_boxes_checked(self):
        # Return TRUE if all channel boxes are checked, FALSE otherwise
        return (
            self.chaOneBox.checkState()
            == self.chaTwoBox.checkState()
            == self.chaZBox.checkState()
            == Qt.CheckState.Checked
        )

    def all_boxes_unchecked(self):
        # Return TRUE if all channel boxes are checked, FALSE otherwise
        return (
            self.chaOneBox.checkState()
            == self.chaTwoBox.checkState()
            == self.chaZBox.checkState()
            == Qt.CheckState.Unchecked
        )

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
        if self.chaOneBox.isChecked():
            channelsChecked[0] = channelOne
        if self.chaTwoBox.isChecked():
            channelsChecked[1] = channelTwo
        if self.chaZBox.isChecked():
            channelsChecked[2] = channelZ

        stationInfo.append(channelsChecked)

        return stationInfo
