from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QCheckBox, QFileDialog, QSpacerItem, QMessageBox)
from PyQt5.QtCore import *
from PyQt5.QtGui import *

app = QApplication([])

mainWindow = QWidget()
mainWindow.show()

app.exec_()