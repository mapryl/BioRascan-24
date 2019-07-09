from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
from struct import unpack
import time

# import serial

# nice COM port emulator: https://www.virtual-serial-port.org/
# QThread the right way http://qaru.site/questions/237794/example-of-the-right-way-to-use-qthread-in-pyqt


class SerialPortReader(QtCore.QObject):
    dataReady = pyqtSignal(list, list, list)
    timeUpdate = pyqtSignal(int)

    def __init__(self):
        super(self.__class__, self).__init__(None)

        self.fullReset()
        self.dt_ms = 20

        self.port1 = QSerialPort()
        self.port2 = QSerialPort()

        self.port1.readyRead.connect(self.OnPortRead)
        self.port2.readyRead.connect(self.OnPortRead)

    @QtCore.pyqtSlot(int)
    def startListen(self, dataReadyInterval, portName):
        self.fullReset()
        self.dataReadyInterval = dataReadyInterval * 1000
        self.port1.setPortName(portName)
        if self.port1.open(QIODevice.ReadWrite):
            self.port1.setBaudRate(34800)
            time.sleep(2)
            self.port1.write(b'5')
        else:
            raise IOError("Cannot connect to device on port COM3")

    @QtCore.pyqtSlot()
    def stopListen(self):
        self.port1.write(b'0')
        self.port1.close()
        # self.port2.close()я

    @QtCore.pyqtSlot()
    def OnPortRead(self):
        # print(self.port1.bytesAvailable(), self.port2.bytesAvailable())
        while self.port1.bytesAvailable() > 4:
            a0_mV = (unpack('<H', self.port1.read(2))[0])  # ads voltage = 2 bytes
            a1_mV = (unpack('<H', self.port1.read(2))[0])

            self.a_ch0.append(a0_mV)
            self.a_ch1.append(a1_mV)

            self.T_ms += self.dt_ms;
            self.T_meas.append(self.T_ms)

            if (self.T_ms % 1000 == 0):
                self.timeUpdate.emit(self.T_ms)

            if (self.T_ms % self.dataReadyInterval == 0):
                self.dataReady.emit(self.a_ch0, self.a_ch1, self.T_meas)
                self.reset()

            print("recieved data:", a0_mV, a1_mV, self.T_ms / 1000)

    def reset(self):
        self.a_ch0 = []
        self.a_ch1 = []
        self.T_meas = []

    def fullReset(self):
        self.reset()
        self.T_ms = 0