#! /usr/bin/python
# Filename: julday.py

import argparse
import datetime

###############################################################################
#
# Julday: Find Julian days from a calendar day and calendar day from Julian Day
#
# Update (12/05/2011): Program is now more modularized for import from other
#   programs. Got rid of month names (e.g. 'January', 'February'), and replaced
#   these with months in numerical format. This was done for simplification.
#
# Sam Fortson
# 18 October 2011
# VT Department of Geosciences
#
###############################################################################

#
# Global constants
#
JANUARY = "01"
MONTH_NAMES = [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
]
MONTH_DAYS = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
LEAP_DAYS = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]


#
# Return True if year is a leap year, False otherwise
#
def isleapyear(year):
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


#
# Return the calendar day corresponding to Julian day and year
#
# Days are now padded with zeros.
#
def dayofyear(year, day):
    month = 0

    if isleapyear(year):
        days = LEAP_DAYS
    else:
        days = MONTH_DAYS

    while days[month] < day:
        month = (month + 1) % 12

    if day <= days[0]:
        return str(MONTH_NAMES[month]).zfill(2) + str(day).zfill(2) + str(year).zfill(4)
    return (
        str(MONTH_NAMES[month]).zfill(2)
        + str(day - days[month - 1]).zfill(2)
        + str(year).zfill(4)
    )


#
# Return Julian day corresponding to Calendar year, month, and day
#
def calcday(year, month, day):
    if isleapyear(year):
        days = LEAP_DAYS
    else:
        days = MONTH_DAYS
    if MONTH_NAMES[month - 1] == JANUARY:
        return day
    else:
        return days[month - 2] + day


#
# Read command-line options and call correct methods
#
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert calendar day into Julian day and convert Julian day into calendar"
            " day. If no arguments are specified today's date is the output."
        ),
    )
    parser.add_argument(
        "-j",
        metavar="MMDDYYYY",
        nargs=1,
        help="Return Julian day for calendar date MMDDYYYY",
    )
    parser.add_argument(
        "-c",
        metavar="DDDYYYY",
        nargs=1,
        help="Return calendar day for Julian date DDDYYYY",
    )

    args = parser.parse_args()
    print(args)
    if args.j:
        date = args.j
        if len(date) < 8:
            print("Warning: Date must be in the format MMDDYYYY")
        else:
            print(
                "Julian Day:                    "
                f" {calcday(int(date[4:]), int(date[0:2]), int(date[2:4]))}"
            )

    if args.c:
        date = args.c
        if len(date) < 7:
            print("Warning: Julian date must be in the format DDDYYYY")
        else:
            print(f"Calenday Day: {dayofyear(int(date[3:]), int(date[0:3]))}")

    if args.j is None and args.c is None:
        now = datetime.datetime.now()
        str(now)
        print(
            "Julian Day:                "
            f" {calcday(int(now.year), int(now.month), int(now.day))}"
        )
        print(
            "Calenday Day:                "
            f" {MONTH_NAMES[int(now.month-1)] + str(now.day) + str(now.year)}"
        )


#
# Call main() when script is invoked
#
if __name__ == "__main__":
    main()

# End of julday.py
