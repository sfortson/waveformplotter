"""Widget for selecting which stations are active."""

from typing import List

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QWidget


class StationCheckBox(QWidget):
    """StationCheckBox is a class for a widget that displays checkboxes of station
    names that can be toggled on and off.

    :param sta: Station name
    :type sta: str
    :param cha1: Channel 1 name
    :type cha1: str
    :param cha2: Channel 2 name
    :type cha2: str
    :param chaz: Z Channel name
    :type chaz: str
    :param parent: Parent widget
    :type parent: QWidget
    """

    def __init__(
        self, sta: str, cha1: str, cha2: str, chaz: str, parent: QWidget
    ):  # pylint: disable=too-many-arguments
        # Init the base class
        QWidget.__init__(self, parent)

        # Create checkboxes
        self.sta_box = QCheckBox(str(sta))
        self.cha_one_box = QCheckBox(str(cha1))
        self.cha_two_box = QCheckBox(str(cha2))
        self.cha_z_box = QCheckBox(str(chaz))

        self._create_checkboxes()

    def _create_checkboxes(self) -> None:
        # Create layout for checkboxes
        h_box = QHBoxLayout(self)
        # Add Checkboxes to layout
        h_box.addWidget(self.sta_box)
        h_box.addWidget(self.cha_one_box)
        h_box.addWidget(self.cha_two_box)
        h_box.addWidget(self.cha_z_box)
        # Set this widget's layout and groupbox
        self.setLayout(h_box)

        # Connect boxes with slots and set station box to be a tristate
        self.sta_box.stateChanged.connect(self.sta_box_checked)
        self.cha_one_box.stateChanged.connect(self.channel_box_checked)
        self.cha_two_box.stateChanged.connect(self.channel_box_checked)
        self.cha_z_box.stateChanged.connect(self.channel_box_checked)

        # Set the channel Z checkbox to true (this is the default behavior)
        self.cha_z_box.setCheckState(Qt.CheckState.Checked)

    @pyqtSlot(Qt.CheckState)
    def sta_box_checked(self, state: Qt.CheckState) -> None:
        """Set the behavior of the station check box when
        its state changes

        :param state: State of check box
        :type state: Qt.CheckState
        """
        if state == Qt.CheckState.Checked:
            self.check_all()
        elif state == Qt.CheckState.Unchecked:
            self.uncheck_all()

    @pyqtSlot(Qt.CheckState)
    def channel_box_checked(self, state: Qt.CheckState) -> None:
        """Set the behavior of the channel check boxes when
        their state changes

        :param state: Check box state
        :type state: Qt.CheckState
        """
        if state == Qt.CheckState.Checked:
            self.sta_box.setCheckState(Qt.CheckState.PartiallyChecked)
            if self.all_boxes_checked():
                self.sta_box.setCheckState(Qt.CheckState.Checked)
        if state == Qt.CheckState.Unchecked:
            self.sta_box.setCheckState(Qt.CheckState.PartiallyChecked)
            if self.all_boxes_unchecked():
                self.sta_box.setCheckState(Qt.CheckState.Unchecked)

    def check_all(self) -> None:
        """Check all of the channel boxes"""
        self.cha_one_box.setCheckState(Qt.CheckState.Checked)
        self.cha_two_box.setCheckState(Qt.CheckState.Checked)
        self.cha_z_box.setCheckState(Qt.CheckState.Checked)

    def uncheck_all(self) -> None:
        """Uncheck all of the channel boxes"""
        self.cha_one_box.setCheckState(Qt.CheckState.Unchecked)
        self.cha_two_box.setCheckState(Qt.CheckState.Unchecked)
        self.cha_z_box.setCheckState(Qt.CheckState.Unchecked)

    def all_boxes_checked(self) -> bool:
        """Return TRUE if all channel boxes are checked, FALSE otherwise

        :return: Whether or not all channel boxes are checked
        :rtype: bool
        """
        return (
            self.cha_one_box.checkState()
            == self.cha_two_box.checkState()
            == self.cha_z_box.checkState()
            == Qt.CheckState.Checked
        )

    def all_boxes_unchecked(self) -> bool:
        """Return TRUE if all channel boxes are unchecked, FALSE otherwise

        :return: Whether or not all channel boxes are unchecked
        :rtype: bool
        """
        return (
            self.cha_one_box.checkState()
            == self.cha_two_box.checkState()
            == self.cha_z_box.checkState()
            == Qt.CheckState.Unchecked
        )

    def get_checked_channels(self) -> List[str]:
        """Return the channels checked by the user in list format

        :return: List of channels checked by the user
        :rtype: List[str]
        """
        station_info = []

        # Init channelsChecked
        channels_checked = ["Null", "Null", "Null"]

        station = str(self.sta_box.text())
        channel_one = str(self.cha_one_box.text())
        channel_two = str(self.cha_two_box.text())
        channel_z = str(self.cha_z_box.text())

        station_info.append(station)
        if self.cha_one_box.isChecked():
            channels_checked[0] = channel_one
        if self.cha_two_box.isChecked():
            channels_checked[1] = channel_two
        if self.cha_z_box.isChecked():
            channels_checked[2] = channel_z

        station_info.append(channels_checked)

        return station_info
