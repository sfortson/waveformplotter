"""Group box widget for selecting start and end times to be viewed."""

from PyQt6.QtCore import QDate, QDateTime, QTime
from PyQt6.QtWidgets import QDateTimeEdit, QGridLayout, QGroupBox, QLabel, QWidget

from helpers.julday import dayofyear


class TimeSelector(QGroupBox):
    """
    TimeSelector subclasses QGroupBox to create a widget for selecting start and end times.

    :param float start_time: Start time
    :param float end_time: End time
    :param QWidget parent: Parent widget
    """

    def __init__(self, start_time: float, end_time: float, parent: QWidget):
        # Init the base class
        QGroupBox.__init__(self, "Select Start and End Times", parent)

        # Define class variables
        self.start_date_time = QDateTimeEdit(self)
        self.end_date_time = QDateTimeEdit(self)
        min_date, max_date = self._init_dates_and_times(start_time, end_time)

        # Init the widgets
        self._init_widgets(min_date, max_date)

    def _init_dates_and_times(self, start_time: float, end_time: float) -> None:
        """
        Get the start time of the seed file.

        :param float start_time: Start time
        :param float end_time: End time
        """
        start_tmp = start_time.split(",")
        start_year = str(start_tmp[0])
        start_julian_day = str(start_tmp[1])
        start_full_time = str(start_tmp[2])
        start_hour = start_full_time.split(":", maxsplit=1)[0]
        start_minute = start_full_time.split(":")[1]
        start_second = float(start_full_time.split(":")[2])
        start_calday = dayofyear(int(start_year), int(start_julian_day))
        start_month = start_calday[:2]
        start_day = start_calday[2:4]

        # Get the end time of the seed file
        end_tmp = end_time.split(",")
        end_year = str(end_tmp[0])
        end_julian_day = str(end_tmp[1])
        end_full_time = str(end_tmp[2])
        end_hour = end_full_time.split(":", maxsplit=1)[0]
        end_minute = end_full_time.split(":")[1]
        end_second = float(end_full_time.split(":")[2])
        end_calday = dayofyear(int(end_year), int(end_julian_day))
        end_month = end_calday[:2]
        end_day = end_calday[2:4]

        # Set min and max dates for QDateTimeEdits
        min_date = QDate(int(start_year), int(start_month), int(start_day))
        max_date = QDate(int(end_year), int(end_month), int(end_day))

        # Set min and max times for QDateTimeEdits
        self.min_time = QTime(
            int(start_hour), int(start_minute), int(round(start_second))
        )
        self.max_time = QTime(int(end_hour), int(end_minute), int(round(end_second)))

        # Set min and max QDateTimes for QDateTimeEdits
        self.minimum_date_time = QDateTime(
            min_date,
            QTime(int(start_hour), int(start_minute), int(round(start_second))),
        )
        self.maximum_date_time = QDateTime(
            max_date,
            QTime(int(end_hour), int(end_minute), int(round(end_second))),
        )

        return min_date, max_date

    def _init_widgets(self, min_date, max_date):
        self.start_date_time.setMinimumDate(min_date)
        self.start_date_time.setMaximumDate(max_date)
        self.start_date_time.setDateTime(self.minimum_date_time)
        self.end_date_time.setMinimumDate(min_date)
        self.end_date_time.setMaximumDate(max_date)
        self.end_date_time.setDateTime(self.minimum_date_time)

        # Set Layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Start Time:"), 0, 0)
        layout.addWidget(self.start_date_time, 0, 1)
        layout.addWidget(QLabel("End Time:"), 1, 0)
        layout.addWidget(self.end_date_time, 1, 1)
        self.setLayout(layout)

    def get_start_datetime(self) -> QDateTime:
        """
        Get the start datetime.

        :return: Start date and time
        :rtype: QDateTime
        """
        if self.start_date_time.dateTime() >= self.minimum_date_time:
            return self.start_date_time.dateTime()
        return self.minimum_date_time

    def get_end_datetime(self) -> QDateTime:
        """
        Get the end datetime.

        :return: End date and time
        :rtype: QDateTime
        """
        if self.end_date_time.dateTime() <= self.maximum_date_time:
            return self.end_date_time.dateTime()
        return self.maximum_date_time

    def get_interval_time(self) -> int:
        """
        Get number of seconds between start and end times.

        :return: Interval time
        :rtype: int
        """
        return self.get_start_datetime().secsTo(self.get_end_datetime())
