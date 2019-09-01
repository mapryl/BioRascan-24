from PyQt5.QtWidgets import (QDialog, QLabel, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QCheckBox, QFileDialog, QSpacerItem, QMessageBox, QComboBox, QInputDialog, QPlainTextEdit)

from PyQt5.QtCore import *

class SettingsWidget(QDialog):
    settigsApplied = pyqtSignal(float, float, float, float)

    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)

        self.setWindowTitle('Расширенные настройки')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # remove help button from top right window corner

        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        self.settingsLayout = QGridLayout()
        self.settingsLayout.setSpacing(20)
        self.settingsLayout.setContentsMargins(40, 20, 40, 10)
        mainLayout.addLayout(self.settingsLayout, 1, 1)

        mainLayout.setRowStretch(0, 1)         # empty space above ui
        mainLayout.setRowStretch(1, 0)         # ui
        mainLayout.setRowStretch(2, 1)         # empty space below ui
        mainLayout.setColumnStretch(0, 1)      # empty space to the right from ui
        mainLayout.setColumnStretch(1, 0)      # ui
        mainLayout.setColumnStretch(2, 1)      # empty space to the left from ui

        self.lhf = 1;
        self.hhf = 2;
        self.lbf = 0.1;
        self.hbf = 1;

        lowHeartFreqLabel = QLabel("Нижняя частота сердечных сокращений")
        self.lowHeartFreqEdit = QLineEdit()
        unitsLabel1 = QLabel('гц')
        unitsLabel1.setObjectName('secondary')
        self.settingsLayout.addWidget(lowHeartFreqLabel, 0, 0)
        self.settingsLayout.addWidget(self.lowHeartFreqEdit, 0, 1)
        self.settingsLayout.addWidget(unitsLabel1, 0, 2)
        self.lowHeartFreqEdit.setText(str(self.lhf))

        highHeartFreqLabel = QLabel("Верхняя частота сердечных сокращений")
        self.highHeartFreqEdit = QLineEdit()
        unitsLabel2 = QLabel('гц')
        unitsLabel2.setObjectName('secondary')
        self.settingsLayout.addWidget(highHeartFreqLabel, 1, 0)
        self.settingsLayout.addWidget(self.highHeartFreqEdit, 1, 1)
        self.settingsLayout.addWidget(unitsLabel2, 1, 2)
        self.highHeartFreqEdit.setText(str(self.hhf))

        lowBreathFreqLabel = QLabel("Нижняя частота дыхания")
        self.lowBreathFreqEdit = QLineEdit()
        unitsLabel3 = QLabel('гц')
        unitsLabel3.setObjectName('secondary')
        self.settingsLayout.addWidget(lowBreathFreqLabel, 2, 0)
        self.settingsLayout.addWidget(self.lowBreathFreqEdit, 2, 1)
        self.settingsLayout.addWidget(unitsLabel3, 2, 2)
        self.lowBreathFreqEdit.setText(str(self.lbf))

        highBreathFreqLabel = QLabel("Верхняя частота дыхания")
        self.highBreathFreqEdit = QLineEdit()
        unitsLabel4 = QLabel('гц')
        unitsLabel4.setObjectName('secondary')
        self.settingsLayout.addWidget(highBreathFreqLabel, 3, 0)
        self.settingsLayout.addWidget(self.highBreathFreqEdit, 3, 1)
        self.settingsLayout.addWidget(unitsLabel4, 3, 2)
        self.highBreathFreqEdit.setText(str(self.hbf))

        buttonsLayout = QHBoxLayout()

        okButton = QPushButton('ПРИНЯТЬ')
        buttonsLayout.addWidget(okButton)
        okButton.clicked.connect(self.onOk)

        cancelButton = QPushButton('ОТМЕНА')
        buttonsLayout.addWidget(cancelButton)
        cancelButton.clicked.connect(self.onCancel)

        self.settingsLayout.setRowMinimumHeight(4, 30) # add some space

        self.settingsLayout.addLayout(buttonsLayout, 5, 0, 1, 3)

    @pyqtSlot()
    def onOk(self):
        self.close()

    @pyqtSlot()
    def onCancel(self):
        self.close()