from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)


class SetYLimWidget(QWidget):
    # Create signals
    set_clicked = pyqtSignal(int, name="SetClicked")

    def __init__(self, widget_parent=None):
        # Init the base class
        QWidget.__init__(self, widget_parent)

        # Set the Widgets
        self.init_widgets()

    def init_widgets(self):
        # Init the layout and widgets
        hbox = QHBoxLayout(self)
        label = QLabel("Set y-limit:")
        self.line = QLineEdit()
        button = QPushButton("Set")

        # Set default line edit text
        self.line.setText("0")

        # Add widgets to the layout
        hbox.addWidget(label)
        hbox.addWidget(self.line)
        hbox.addWidget(button)

        # Set this widget's layout to hbox
        self.setLayout(hbox)

        # Connect set button
        button.clicked.connect(self.set_button_clicked)

    def set_button_clicked(self):
        # Slot controlling what happens when set button is clicked,
        # or Enter key is pressed
        lineValue = self.get_line_value()
        self.set_clicked.emit(lineValue)

    def get_line_value(self):
        # Return the integer value of what the user entered in the line edit
        return int(self.line.text())

    def set_line_value(self, yMax):
        # Set line edit value to yMax
        self.line.setText(QtCore.QString(yMax))

    def keyPressEvent(self, event):
        # Allow the user to hit enter when setting y-limit
        if event.matches(QKeySequence.StandardKey.InsertParagraphSeparator):
            self.set_button_clicked()
