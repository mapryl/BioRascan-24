from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QCheckBox, QFileDialog, QSpacerItem, QMessageBox)
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from SerialPortReader import *
from SerialPortWriter import *

import pyqtgraph as pg
import numpy as np

class PlotWidget(pg.GraphicsWindow):
    def __init__(self):
        super(self.__class__, self).__init__(None)

        self.setWindowTitle('pyqtgraph example: Scrolling Plots')

        p = self.addPlot()
        self.data = np.zeros(300)
        self.curve = p.plot(self.data, pen=pg.mkPen(QColor('#5961FF'), width=2))
        self.ptr = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(250)

    def update(self):
        self.data[:-1] = self.data[1:]
        self.data[-1] = np.random.normal()

        self.ptr += 1
        self.curve.setData(self.data)
        self.curve.setPos(self.ptr , 0)

class ExperimentData:
    def __init__(self):
        self.a_ch0 = []
        self.a_ch1 = []
        self.a_ch20 = []
        self.a_ch21 = []
        self.T_meas = []

    def append(self, a_ch0, a_ch1, a_ch20, a_ch21, T_meas):
        self.a_ch0 += a_ch0
        self.a_ch1 += a_ch1
        self.a_ch20 += a_ch20
        self.a_ch21 += a_ch21
        self.T_meas += T_meas

class MainWindow(QWidget):
    processData = pyqtSignal(list, list, list, list, list)
    def __init__(self):
        super(self.__class__, self).__init__(None)

        self.reader = SerialPortReader()
        self.writer = SerialPortWriter()
        self.experimentData = ExperimentData()

        self.initGUI()

        self.plotWidget = PlotWidget()
        self.rightLayout.addWidget(self.plotWidget)

        self.reader.timeUpdate.connect(self.onTimeUpdate)

    @QtCore.pyqtSlot(list, list, list, list, list)
    def onDataReady(self, a_ch0, a_ch1, a_ch20, a_ch21, T_meas):
        self.experimentData.append(a_ch0, a_ch1, a_ch20, a_ch21, T_meas)
        self.processData.emit(a_ch0, a_ch1, a_ch20, a_ch21, T_meas)

    @QtCore.pyqtSlot(int)
    def onTimeUpdate(self, time):
        time = QTime.fromMSecsSinceStartOfDay(time)
        self.timeLabel.setText(time.toString())

    def initGUI(self):
        self.setWindowTitle('БиоРАСКАН-24')

        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        leftLayout = QVBoxLayout()
        leftLayout.setSpacing(20)
        mainLayout.addLayout(leftLayout, 1, 1, Qt.AlignCenter)

        self.rightLayout = QVBoxLayout()
        mainLayout.addLayout(self.rightLayout, 1, 2, Qt.AlignCenter)

        mainLayout.setRowStretch(0, 1)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(3, 1)

        # settings layout
        settingsLayout = QGridLayout()
        leftLayout.addLayout(settingsLayout)

        validator = QIntValidator(1, 60)
        lengthSettingsText = QLabel('Длительность эксперимента')
        lengthSettingsEdit = QLineEdit('1')
        lengthSettingsEdit.setValidator(validator)
        lmin = QLabel('мин')
        lmin.setObjectName("secondary")

        settingsLayout.addWidget(lengthSettingsText, 0, 0)
        settingsLayout.addWidget(lengthSettingsEdit, 0, 1)
        settingsLayout.addWidget(lmin, 0, 2)

        intervalLayoutText = QLabel('Интервал расчета')
        self.intervalLayoutEdit = QLineEdit('1')
        self.intervalLayoutEdit.setValidator(validator)
        imin = QLabel('мин')
        imin.setObjectName("secondary")
        settingsLayout.addWidget(intervalLayoutText, 1, 0)
        settingsLayout.addWidget(self.intervalLayoutEdit, 1, 1)
        settingsLayout.addWidget(imin, 1, 2)

        # back to main layout
        soundCheckBox = QCheckBox('Звуковое оповещение')
        leftLayout.addWidget(soundCheckBox)

        self.timeLabel = QLabel('00:00:00')
        self.timeLabel.setObjectName('timeLabel')
        leftLayout.addWidget(self.timeLabel)
        leftLayout.setAlignment(self.timeLabel, Qt.AlignHCenter)

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
        self.startStopButton = QPushButton('ЗАПУСК')
        self.startStopButton.setCheckable(True)
        saveButton = QPushButton('СОХРАНИТЬ')
        saveButton.clicked.connect(self.onSaveButtonClicked)
        buttonLayout.addWidget(self.startStopButton)
        buttonLayout.addSpacing(20)
        buttonLayout.addWidget(saveButton)

        self.startStopButton.toggled.connect(self.onButtonClick)
        self.startStopButton.clicked.connect(self.writer.startSend)

    @QtCore.pyqtSlot(bool)
    def onButtonClick(self, toggled):
        if toggled:
            self.startStopButton.setText('СТОП')
            interval_time = int(self.intervalLayoutEdit.text())
            self.reader.startListen(interval_time)
        else:
            self.startStopButton.setText('ЗАПУСК')
            self.reader.stopListen()

    @QtCore.pyqtSlot()
    def onSaveButtonClicked(self):
        QFileDialog.getSaveFileName()

    def closeEvent(self, event):
        return
        reply = QMessageBox.question(self, 'Message',
            "Вы уверены, что хотите выйти?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

app = QApplication([])

# load Google Roboto fonts
font_db = QFontDatabase()
font_db.addApplicationFont("/fonts/Roboto-Regular.ttf")
font_db.addApplicationFont("/fonts/Roboto-Bold.ttf")
font_db.addApplicationFont("/fonts/Roboto-Thin.ttf")

# apply Qt stylesheet
stylesheet = open("stylesheet.qss").read()
app.setStyleSheet(stylesheet)

pg.setConfigOption('background', 'w')

mainWindow = MainWindow()
mainWindow.show()

app.exec_()


