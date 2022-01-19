#!/usr/bin/env python

from helpers.julday import dayofyear
from PyQt6.QtCore import QDate, QDateTime, QTime
from PyQt6.QtWidgets import QDateTimeEdit, QGridLayout, QGroupBox, QLabel


class TimeSelector(QGroupBox):
    def __init__(self, startTime, endTime, parent):
        # Init the base class
        QGroupBox.__init__(self, "Select Start and End Times", parent)

        # Define class variables
        self.startDateTime = QDateTimeEdit(self)
        self.endDateTime = QDateTimeEdit(self)
        self.init_dates_and_times(startTime, endTime)

        # Init the widgets
        self.init_widgets(startTime, endTime)

    def init_dates_and_times(self, startTime, endTime):
        # Get the start time of the seed file
        stmp = startTime.split(",")
        syear = str(stmp[0])
        sjulianDay = str(stmp[1])
        sfullTime = str(stmp[2])
        shour = sfullTime.split(":")[0]
        sminute = sfullTime.split(":")[1]
        ssecond = float(sfullTime.split(":")[2])
        scalday = dayofyear(int(syear), int(sjulianDay))
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
        ecalday = dayofyear(int(eyear), int(ejulianDay))
        emonth = ecalday[:2]
        eday = ecalday[2:4]

        # Set min and max dates for QDateTimeEdits
        self.minDate = QDate(int(syear), int(smonth), int(sday))
        self.maxDate = QDate(int(eyear), int(emonth), int(eday))

        # Set min and max times for QDateTimeEdits
        self.minTime = QTime(int(shour), int(sminute), int(round(ssecond)))
        self.maxTime = QTime(int(ehour), int(eminute), int(round(esecond)))

        # Set min and max QDateTimes for QDateTimeEdits
        self.minimumDateTime = QDateTime(
            self.minDate,
            QTime(int(shour), int(sminute), int(round(ssecond))),
        )
        self.maximumDateTime = QDateTime(
            self.maxDate,
            QTime(int(ehour), int(eminute), int(round(esecond))),
        )

    def init_widgets(self, startTime, endTime):
        self.startDateTime.setMinimumDate(self.minDate)
        self.startDateTime.setMaximumDate(self.maxDate)
        self.startDateTime.setDateTime(self.minimumDateTime)
        self.endDateTime.setMinimumDate(self.minDate)
        self.endDateTime.setMaximumDate(self.maxDate)
        self.endDateTime.setDateTime(self.minimumDateTime)

        # Set Layout
        layout = QGridLayout()
        layout.addWidget(QLabel("Start Time:"), 0, 0)
        layout.addWidget(self.startDateTime, 0, 1)
        layout.addWidget(QLabel("End Time:"), 1, 0)
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
        return self.get_start_datetime().secsTo(self.get_end_datetime())
