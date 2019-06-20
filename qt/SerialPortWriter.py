from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtSerialPort import *
from struct import pack

class SerialPortWriter(QtCore.QObject):
    def __init__(self):
        super(self.__class__, self).__init__(None)

        self.port1 = QSerialPort()
        self.port2 = QSerialPort()
        self.timer = QTimer()

        self.timer.timeout.connect(self.onTimeout)

    @QtCore.pyqtSlot()
    def startSend(self):
        print("dsfgsdgf")
        self.port1.setPortName('COM6')
        self.port1.setBaudRate(QSerialPort.Baud38400)

        self.port2.setPortName('COM7')
        self.port2.setBaudRate(QSerialPort.Baud38400)

        self.port1.open(QIODevice.WriteOnly)
        self.port2.open(QIODevice.WriteOnly)

        self.timer.start(4)

    def onTimeout(self):
        dataPacked11 = pack("<H", 1)
        dataPacked12 = pack("<H", 2)

        self.port1.write(dataPacked11)
        self.port1.write(dataPacked12)

        self.port2.write(dataPacked11)
        self.port2.write(dataPacked12)