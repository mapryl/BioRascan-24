from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QCheckBox, QFileDialog, QSpacerItem, QMessageBox, QComboBox)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QSoundEffect

from SerialPortReader import *
from SerialPortWriter import *

import pyqtgraph as pg
import numpy as np

from BreathingRateCounter import breath_rate_counter
from COMReader import serial_ports
from pip._internal import exceptions

class RascanWorker(QObject):

    dataProcessed = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    @QtCore.pyqtSlot(list, list, int)
    def doWork(self, a_ch0, a_ch1, t_interval):

        a_ch0 = np.array(a_ch0)
        a_ch1 = np.array(a_ch1)

        a_ch0 = a_ch0 / 8000
        a_ch1 = a_ch1 / 8000

        try:
            hr, br = breath_rate_counter(a_ch0, a_ch1, t_interval)
        except:
            hr, br = 0, 0

        self.dataProcessed.emit(hr, br)

class PlotWidget(pg.GraphicsWindow):
    def __init__(self, maxY):
        super(self.__class__, self).__init__(None)

        self.setWindowTitle('pyqtgraph example: Scrolling Plots')

        p = self.addPlot()
        self.plot = p
        self.dataSize = 10
        self.data = []
        self.curve = p.plot(self.data, pen=pg.mkPen(QColor('#5961FF'), width=2))
        self.ptr = 0

        font = QFont('roboto')
        font.setPixelSize(20)
        p.getAxis("bottom").tickFont = font
        p.getAxis("bottom").setStyle(tickTextOffset=30)
        p.getAxis("left").tickFont = font
        p.getAxis("left").setStyle(tickTextOffset=30)

        p.setYRange(0, maxY, padding = 0)

    def appendPoint(self, value):
        if len(self.data) < self.dataSize:
            self.data.append(value)
        else:
            self.data[:-1] = self.data[1:]
            self.data[-1] = value

            self.ptr += 1
        self.curve.setData(self.data)
        self.curve.setPos(self.ptr, 0)

    def reset(self):
        self.data = [0]
        self.ptr = 0
        self.curve.setData(self.data)
        self.curve.setPos(self.ptr, 0)
        self.data = []
        self.ptr = 0
        self.curve.setData(self.data)
        self.curve.setPos(self.ptr, 0)

class ExperimentData:
    def __init__(self):
        self.reset()

    def appendData(self, a_ch0, a_ch1, T_meas):
        self.a_ch0 += a_ch0
        self.a_ch1 += a_ch1
        self.T_meas += T_meas
        self.needToSave = True

    def appentDataToTxt(self, a_ch0, a_ch1, T_meas):
        with open('text.txt', 'a') as file:
            for i in range(0, len(a_ch0)):
                file.write(str(a_ch0[i]) + ' ' + str(a_ch1[i]) + ' ' + str(T_meas[i]) + '\n')
        self.needToSave = False

    def reset(self):
        self.a_ch0 = []
        self.a_ch1 = []
        self.T_meas = []
        self.needToSave = False

    def saveIfNeeded(self):
        if self.needToSave:
            self.saveToFile()

    def saveToFile(self):
        if len(self.T_meas) != 0:
            fileName = QFileDialog.getSaveFileName(None, "Save unsaved data to file", QDir(".").canonicalPath(), "NPZ(*.npz)")
            np.savez_compressed(fileName[0], ch0=self.a_ch0, ch1=self.a_ch1,
                                T=self.T_meas)
            self.needToSave = False

class MyIntValidator(QIntValidator):
    def __init__(self, min, max):
        super(self.__class__, self).__init__(min, max)
        self.min = min

    def fixup(self, s):
        return str(self.min)

class MainWindow(QWidget):
    processData = pyqtSignal(list, list, int)
    def __init__(self):
        super(self.__class__, self).__init__(None)

        self.reader = SerialPortReader()
        self.writer = SerialPortWriter()
        self.experimentData = ExperimentData()

        self.initGUI()
        self.initSound()

        self.createWorkerThread()

        self.heartRatePlotWidget = PlotWidget(70)
        self.breathRatePlotWidget = PlotWidget(40)
        self.rightLayout.addWidget(self.heartRatePlotWidget)
        self.rightLayout.addWidget(self.breathRatePlotWidget)

        self.reader.timeUpdate.connect(self.onTimeUpdate)
        self.reader.dataReady.connect(self.onDataReady)

    @QtCore.pyqtSlot(list, list, list)
    def onDataReady(self, a_ch0, a_ch1, T_meas):
        if self.experimentLength < 5:
            self.experimentData.appendData(a_ch0, a_ch1, T_meas)
        else:
            self.experimentData.appentDataToTxt(a_ch0, a_ch1, T_meas)
        self.processData.emit(a_ch0, a_ch1, self.interval_time)

    @QtCore.pyqtSlot(int)
    def onTimeUpdate(self, time):
        time = self.experimentLength*60*1000 - time
        qtTime = QTime.fromMSecsSinceStartOfDay(time)
        self.timeLabel.setText(qtTime.toString())

        if time == 0:
            self.startStopButton.toggle()
            if self.soundCheckBox.isChecked():
                self.sound.play()

    def createWorkerThread(self):
        self.rascanWorker = RascanWorker()
        self.workerThread = QThread()
        self.rascanWorker.moveToThread(self.workerThread)
        self.workerThread.start()

        self.processData.connect(self.rascanWorker.doWork)
        self.rascanWorker.dataProcessed.connect(self.onRascanDataProcessed)

    def initSound(self):
        self.sound = QSoundEffect()
        base_url = QUrl.fromLocalFile(QDir(".").canonicalPath() + "/")
        file_path = base_url.resolved(QUrl("bzzz.wav"))

        self.sound.setSource(file_path)
        self.sound.setVolume(1)

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

        lengthSettingsText = QLabel('Длительность эксперимента')
        self.lengthSettingsEdit = QLineEdit('1')
        self.lengthSettingsEdit.setValidator(MyIntValidator(1, 30))
        lmin = QLabel('мин')
        lmin.setObjectName("secondary")

        settingsLayout.addWidget(lengthSettingsText, 0, 0)
        settingsLayout.addWidget(self.lengthSettingsEdit, 0, 1)
        settingsLayout.addWidget(lmin, 0, 2)

        intervalLayoutText = QLabel('Интервал расчета')
        self.intervalLayoutEdit = QLineEdit('10')
        self.intervalLayoutEdit.setValidator(MyIntValidator(10, 60))
        imin = QLabel('сек')
        imin.setObjectName("secondary")
        settingsLayout.addWidget(intervalLayoutText, 1, 0)
        settingsLayout.addWidget(self.intervalLayoutEdit, 1, 1)
        settingsLayout.addWidget(imin, 1, 2)

        # back to main layout
        checkBoxLayout = QGridLayout()
        leftLayout.addLayout(checkBoxLayout)

        self.soundCheckBox = QCheckBox('Звуковое оповещение')
        checkBoxLayout.addWidget(self.soundCheckBox, 0, 0)

        self.saveCheckBox = QCheckBox('Запрос на сохранение')
        checkBoxLayout.addWidget(self.saveCheckBox, 1, 0)
        self.saveCheckBox.toggle()

        self.comBox = QComboBox(self)
        COMLayoutText = QLabel('Выбор COM-порта')
        COM_list = serial_ports()
        self.comBox.addItems(COM_list)
        checkBoxLayout.addWidget(COMLayoutText, 0, 1)
        checkBoxLayout.addWidget(self.comBox, 1, 1)

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

        self.heartRateText = QLabel('0')
        self.heartRateText.setObjectName('primary')
        self.heartRateText.setAlignment(Qt.AlignRight)
        infoLayout.addWidget(self.heartRateText)

        udm = QLabel('уд/мин')
        udm.setObjectName('secondary')
        infoLayout.addWidget(udm)

        infoLayout.addSpacing(40)

        chd = QLabel('ЧД')
        chd.setObjectName('leftBar')
        infoLayout.addWidget(chd)

        self.breathRateText = QLabel('0')
        self.breathRateText.setObjectName('primary')
        self.breathRateText.setAlignment(Qt.AlignRight)
        infoLayout.addWidget(self.breathRateText)

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
        #self.startStopButton.clicked.connect(self.writer.startSend)

    @QtCore.pyqtSlot(bool)
    def onButtonClick(self, toggled):
        if toggled:
            if self.saveCheckBox.isChecked():
                self.experimentData.saveIfNeeded()
            self.experimentData.reset()
            self.startStopButton.setText('СТОП')
            self.interval_time = int(self.intervalLayoutEdit.text())
            self.experimentLength = int(self.lengthSettingsEdit.text())
            portName = self.comBox.currentText()
            self.reader.startListen(self.interval_time, portName)
            self.heartRatePlotWidget.reset()
            self.breathRatePlotWidget.reset()
        else:
            self.startStopButton.setText('ЗАПУСК')
            self.reader.stopListen()

    @QtCore.pyqtSlot()
    def onSaveButtonClicked(self):
        self.experimentData.saveToFile()

    @QtCore.pyqtSlot(float, float)
    def onRascanDataProcessed(self, chss, chd):
        self.heartRateText.setText(str(chss))
        self.breathRateText.setText(str(chd))
        self.heartRatePlotWidget.appendPoint(chss)
        self.breathRatePlotWidget.appendPoint(chd)

    def closeEvent(self, event):
        if (self.saveCheckBox.isChecked()):
            self.experimentData.saveIfNeeded()
        event.accept()


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
pg.setConfigOptions(antialias=True)

mainWindow = MainWindow()
mainWindow.show()

app.exec_()


