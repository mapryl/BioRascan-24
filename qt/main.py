from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QCheckBox, QFileDialog, QSpacerItem, QMessageBox)
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from SerialPortReader import *
from SerialPortWriter import *


def onSaveButtonClicked():
    QFileDialog.getSaveFileName()


app = QApplication([])

# load Google Roboto fonts
font_db = QFontDatabase()
font_db.addApplicationFont("/fonts/Roboto-Regular.ttf")
font_db.addApplicationFont("/fonts/Roboto-Bold.ttf")
font_db.addApplicationFont("/fonts/Roboto-Thin.ttf")

# apply Qt stylesheet
stylesheet = open("stylesheet.qss").read()
app.setStyleSheet(stylesheet)


class MainWindow(QWidget):

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Вы уверены, что хотите выйти?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


mainWindow = MainWindow()
mainWindow.setWindowTitle('БиоРАСКАН-24')

mainLayout = QGridLayout()
mainWindow.setLayout(mainLayout)

leftLayout = QVBoxLayout()
leftLayout.setSpacing(20)
mainLayout.addLayout(leftLayout, 1, 1, Qt.AlignCenter)

mainLayout.setRowStretch(0, 1)
mainLayout.setRowStretch(2, 1)
mainLayout.setColumnStretch(0, 1)
mainLayout.setColumnStretch(2, 1)

# settings layout
settingsLayout = QGridLayout()
leftLayout.addLayout(settingsLayout)

validator = QDoubleValidator()
lengthSettingsText = QLabel('Длительность эксперимента')
lengthSettingsEdit = QLineEdit()
lengthSettingsEdit.setValidator(validator)
lmin = QLabel('мин')
lmin.setObjectName("secondary")

settingsLayout.addWidget(lengthSettingsText, 0, 0)
settingsLayout.addWidget(lengthSettingsEdit, 0, 1)
settingsLayout.addWidget(lmin, 0, 2)

intervalLayoutText = QLabel('Интервал расчета')
intervalLayoutEdit = QLineEdit()
intervalLayoutEdit.setValidator(validator)
imin = QLabel('мин')
imin.setObjectName("secondary")
settingsLayout.addWidget(intervalLayoutText, 1, 0)
settingsLayout.addWidget(intervalLayoutEdit, 1, 1)
settingsLayout.addWidget(imin, 1, 2)

# back to main layout
soundCheckBox = QCheckBox('Звуковое оповещение')
leftLayout.addWidget(soundCheckBox)

timeLabel = QLabel('00:01')
timeLabel.setObjectName('timeLabel')
leftLayout.addWidget(timeLabel)
leftLayout.setAlignment(timeLabel, Qt.AlignHCenter)

infoLayout = QHBoxLayout()
infoLayout.setSpacing(20)
leftLayout.addLayout(infoLayout)
infoLayout.addStretch()

chss = QLabel('ЧСС')
chss.setObjectName('leftBar')
infoLayout.addWidget(chss)

heartRateText = QLabel('60')
heartRateText.setObjectName('primary')
infoLayout.addWidget(heartRateText)

udm = QLabel('уд/мин')
udm.setObjectName('secondary')
infoLayout.addWidget(udm)

infoLayout.addSpacing(40)

chd = QLabel('ЧД')
chd.setObjectName('leftBar')
infoLayout.addWidget(chd)

breathRateText = QLabel('21')
breathRateText.setObjectName('primary')
infoLayout.addWidget(breathRateText)

vdm = QLabel('вдох/мин')
vdm.setObjectName('secondary')
infoLayout.addWidget(vdm)

infoLayout.addStretch()

buttonLayout = QHBoxLayout()
leftLayout.addLayout(buttonLayout)
startStopButton = QPushButton('ЗАПУСК')
startStopButton.setCheckable(True)
saveButton = QPushButton('СОХРАНИТЬ')
saveButton.clicked.connect(onSaveButtonClicked)
buttonLayout.addWidget(startStopButton)
buttonLayout.addSpacing(20)
buttonLayout.addWidget(saveButton)

mainWindow.show()

reader = SerialPortReader()
writer = SerialPortWriter()

def onButtonClick(toggled):
    if toggled:
        startStopButton.setText('СТОП')
        reader.startListen()
        global interval_time
        interval_time = intervalLayoutEdit.text()
    else:
        startStopButton.setText('ЗАПУСК')
        reader.stopListen()


startStopButton.toggled.connect(onButtonClick)
startStopButton.clicked.connect(writer.startSend)

#ex = mainWindow()
app.exec_()


