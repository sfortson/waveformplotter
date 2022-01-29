"""Widget for setting y limits."""

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget


class SetYLimWidget(QWidget):
    """
    Widget class for setting y-axis limits.

    :param widget_parent: Parent widget of this widget
    :type widget_parent: QWidget or None
    """

    # Create signals
    set_clicked = pyqtSignal(int, name="SetClicked")

    def __init__(self, widget_parent=None):
        # Init the base class
        QWidget.__init__(self, widget_parent)

        # Set the Widgets
        self._init_widgets()

    def _init_widgets(self) -> None:
        """Init the layout and widgets."""
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

    @pyqtSlot()
    def set_button_clicked(self) -> None:
        """Slot controlling what happens when set button is clicked, or Enter key is pressed."""
        line_value = self.get_line_value()
        self.set_clicked.emit(line_value)

    def get_line_value(self) -> int:
        """
        Return the integer value of what the user entered in the line edit.

        :return: Line value
        :rtype: int
        """
        return int(self.line.text())

    def set_line_value(self, y_max) -> None:
        """Set line edit value to yMax."""
        self.line.setText(str(y_max))

    def keyPressEvent(self, event) -> None:  # pylint: disable=invalid-name
        """
        Allow the user to hit enter when setting y-limit.

        :param QEvent event: KeyPressEvent
        """
        if event.matches(QKeySequence.StandardKey.InsertParagraphSeparator):
            self.set_button_clicked()
