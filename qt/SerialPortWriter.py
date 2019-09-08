from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
from struct import pack
import numpy as np

class SerialPortWriter(QtCore.QObject):
    def __init__(self):
        super(self.__class__, self).__init__(None)

        self.port1 = QSerialPort()
        self.port2 = QSerialPort()
        self.timer = QTimer()

        self.timer.timeout.connect(self.onTimeout)

        rad = np.load('Demkin_br_Rad1_1.npz')
        self.time = rad["T"]
        self.signal1 = rad["ch0"]
        self.signal2 = rad["ch1"]

        self.time = self.time
        self.signal1 = self.signal1
        self.signal2 = self.signal2

        self.index = 0

    @QtCore.pyqtSlot()
    def startSend(self):
        print("dsfgsdgf")
        self.port1.setPortName('COM6')
        self.port1.setBaudRate(QSerialPort.Baud38400)

        #self.port2.setPortName('COM7')
        #self.port2.setBaudRate(QSerialPort.Baud38400)

        self.port1.open(QIODevice.WriteOnly)
        #self.port2.open(QIODevice.WriteOnly)

        self.timer.start(4)

    def stopSend(self):
        self.timer.stop()

    def onTimeout(self):
        index = self.index % len(self.signal1)
        dataPacked11 = pack("<H", self.signal1[index])
        dataPacked12 = pack("<H", self.signal2[index])

        self.port1.write(dataPacked11)
        self.port1.write(dataPacked12)

        self.index += 1

        #self.port2.write(self.signal2[self.index])
        #self.port2.write(self.signal2[self.index])