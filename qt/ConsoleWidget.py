from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

# QTextEdit allows for different line colors but scrolls ugly with new line add
# QPlainTextEdit can only have one text color but scolls nice with line add

class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)

    @QtCore.pyqtSlot(str, 'QColor')
    def printMessage(self, msg, color=None):
        self.moveCursor(QTextCursor.End)
        #if color:
        #    tc = self.textColor()
        #    self.setTextColor(color)
        if msg != "\n":
            msg = "[" + QTime.currentTime().toString() + "] " + msg
        self.insertPlainText(msg)
        #if color:
        #    self.setTextColor(tc)