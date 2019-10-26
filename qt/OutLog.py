from PyQt5.QtGui import *
from PyQt5.QtCore import *


class OutLog(QObject):
    printSignal = pyqtSignal(str, 'QColor')

    def __init__(self, edit, out=None, color=None):
        super(self.__class__, self).__init__(None)

        self.printSignal.connect(edit.printMessage)

        self.edit = edit
        self.old_out = out
        self.color = color

        if not self.color:
            self.color = QColor('#a0a0a0')  # default color

    def write(self, msg):
        self.printSignal.emit(msg, self.color)

        if self.old_out:
            self.old_out.write(msg)

    def flush(self):
        pass
