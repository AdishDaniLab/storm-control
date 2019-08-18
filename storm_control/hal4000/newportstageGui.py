#!/usr/bin/python
#
# @file
#
# GUI for the Newport SMC100 motor controller, with EPI/TIRF options.
#
# Hazen 1/10 (Modified by Gayatri 5/19)
#

import sys

from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSlot, Qt, QTimer

# import html, unicodedata

# try:
#     _fromUtf8 = QStringListModel.fromUtf8
# except AttributeError:
#     _fromUtf8 = lambda s: s

# Debugging
import storm_control.sc_library.hdebug as hdebug

# UIs.
import qtdesigner.storm3_misc_ui as miscControlsUi

# SMC100 motor (for EPI/TIRF)
import storm_control.sc_hardware.newport.SMC100 as SMC100

#
# Misc Control Dialog Box
#


class MiscControl(QtWidgets.QDialog):
    def __init__(self, parameters, parent=None):
        QMainWindow.__init__(self, parent)

        self.debug = 0
        self.move_timer = QTimer(self)
        self.move_timer.setInterval(50)

        if parent:
            self.have_parent = 1
        else:
            self.have_parent = 0

        self.left = 600
        self.top = 300
        self.width = 350
        self.height = 170
        # UI setup
        self.initUI()
        # self.ui = miscControlsUi.Ui_Dialog()
        # self.ui.setupUi(self)

###########################################################################################

        # connect signals

        if self.have_parent:
            self.ui.okButton.setText("Close")
            self.connect(self.ui.okButton, QtCore.SIGNAL(
                "clicked()"), self.handleOk)
        else:
            self.okButton.setText("Quit")
            self.okButton.clicked.connect(self.handleQuit)

        self.EPIButton.clicked.connect(self.goToEPI)
        self.TIRFButton.clicked.connect(self.goToTIRF)
        self.move_timer.timeout.connect(self.updatePosition)
        self.posInput.valueChanged.connect(self.updatePosition)
        self.leftSmallButton.clicked.connect(self.smallLeft)
        self.rightSmallButton.clicked.connect(self.smallRight)
        self.leftLargeButton.clicked.connect(self.largeLeft)
        self.rightLargeButton.clicked.connect(self.largeRight)
        self.tirGoButton.clicked.connect(self.goToX)
        self.rightLarge.clicked.connect(self.largeRightSmall)
        self.leftSmall.clicked.connect(self.smallLeftSmall)
        self.rightSmall.clicked.connect(self.smallRightSmall)
        self.leftLarge.clicked.connect(self.largeLeftSmall)
####################################################################################################

        # set modeless
        self.setModal(False)
        self.home_position = 0.0
        self.epi_position = 17.6
        self.tirf_position = 19.9
        self.jog_size = 0.05
        self.jog_size_small = 0.01

        if parameters:
            self.newParameters(parameters)

        # epi/tir stage init
        self.smc100 = SMC100.SMC100()
        self.position = self.smc100.getPosition()
#        if self.position < 18.0:
#            self.position = self.epi_position
#            self.move()
#        if self.position > 22.0:
#            self.position = self.tirf_position
#            self.move()
        self.setPositionText()


    def initUI(self):

        # Set window title , icon and geometry

        self.setWindowTitle("Newport Stage Control")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('p202.png'))
        # Build the GUI layout here.

        self.EPIButton = QToolButton()
        self.TIRFButton = QToolButton()
        self.leftLargeButton = QToolButton()
        self.leftSmallButton = QToolButton()
        self.rightSmallButton = QToolButton()
        self.rightLargeButton = QToolButton()
        self.leftLarge = QToolButton()
        self.leftSmall = QToolButton()
        self.rightSmall = QToolButton()
        self.rightLarge = QToolButton()
        self.okButton = QPushButton('Quit', self)
        self.positionDisplay = QLabel()
        self.readMe = QLabel()
        self.readMe.setText("EPI : 17.6\nTIRF : 19.9\n\u2BC7 : jog size 0.05\n\u2BC7\u2BC7 : jog size 0.5\n<- : jog size 0.01\n<-- : jog size 0.1")
        self.posInput = QDoubleSpinBox()
        self.tirGoButton = QPushButton('Go to', self)


        self.EPIButton.setText('EPI')
        self.EPIButton.setChecked(False)
        self.TIRFButton.setText('TIRF')
        self.TIRFButton.setChecked(False)
        self.leftLargeButton.setText('\u2BC7\u2BC7')
        self.leftLargeButton.setChecked(False)
        self.leftSmallButton.setText('\u2BC7')
        self.leftSmallButton.setChecked(False)
        self.rightSmallButton.setText('\u2BC8')
        self.rightSmallButton.setChecked(False)
        self.rightLargeButton.setText('\u2BC8\u2BC8')
        self.rightLargeButton.setChecked(False)
        self.leftLarge.setText('<--')
        self.leftLarge.setChecked(False)
        self.leftSmall.setText('<-')
        self.leftSmall.setChecked(False)
        self.rightLarge.setText('-->')
        self.rightLarge.setChecked(False)
        self.rightSmall.setText('->')
        self.rightSmall.setChecked(False)
        self.posInput.setMinimum(0.000)
        self.posInput.setMaximum(25.000)
        self.posInput.singleStep()

        self.tirGoButton.setChecked(False)
        
        # mastergrid = QGridLayout()


        grid = QGridLayout()
        grid.addWidget(self.EPIButton, 0, 0)
        grid.addWidget(self.leftLargeButton, 0, 1)
        grid.addWidget(self.leftSmallButton, 0, 2)
        grid.addWidget(self.rightSmallButton, 0, 3)
        grid.addWidget(self.rightLargeButton, 0, 4)
        grid.addWidget(self.TIRFButton, 0, 5)
        grid.addWidget(self.positionDisplay, 0, 6)
        grid.addWidget(self.leftLarge, 1, 1)
        grid.addWidget(self.leftSmall, 1, 2)
        grid.addWidget(self.rightSmall, 1, 3)
        grid.addWidget(self.rightLarge, 1, 4)
        grid.addWidget(self.readMe, 4, 6)
        grid.addWidget(self.posInput, 3, 5)
        grid.addWidget(self.tirGoButton, 3, 6)
        
        grid.addWidget(self.okButton, 5, 6)
        self.setLayout(grid)

        # mastergrid.addWidget(self.mainControls(), 0, 0)
        # mastergrid.addWidget(self.readMe, 1, 0)
        # self.setLayout(mastergrid)

        self.show()


        
        finish = QAction("Quit", self)
        finish.triggered.connect(self.closeEvent)

    def closeEvent(self, event):
        if self.debug:
            print("closeEvent")
        if self.have_parent:
            event.ignore()
            self.hide()
        else:
            self.quit()

    # def mainControls(self):
    #     '''
    #     Stage control
    #     '''
    #     groupBox = QGroupBox('561')
    #     grid = QGridLayout()

    #     self.EPIButton = QToolButton()
    #     self.TIRFButton = QToolButton()
    #     self.leftLargeButton = QToolButton()
    #     self.leftSmallButton = QToolButton()
    #     self.rightSmallButton = QToolButton()
    #     self.rightLargeButton = QToolButton()
    #     self.leftLarge = QToolButton()
    #     self.leftSmall = QToolButton()
    #     self.rightSmall = QToolButton()
    #     self.rightLarge = QToolButton()
    #     self.okButton = QPushButton('Quit', self)
    #     self.positionDisplay = QLabel()
    #     self.readMe = QLabel()
    #     self.readMe.setText("EPI : 17.6\nTIRF : 19.9\n\u2BC7 : jog size 0.05\n\u2BC7\u2BC7 : jog size 0.5")
    #     self.posInput = QDoubleSpinBox()
    #     self.tirGoButton = QPushButton('Go to', self)


    #     self.EPIButton.setText('EPI')
    #     self.EPIButton.setChecked(False)
    #     self.TIRFButton.setText('TIRF')
    #     self.TIRFButton.setChecked(False)
    #     self.leftLargeButton.setText('\u2BC7\u2BC7')
    #     self.leftLargeButton.setChecked(False)
    #     self.leftSmallButton.setText('\u2BC7')
    #     self.leftSmallButton.setChecked(False)
    #     self.rightSmallButton.setText('\u2BC8')
    #     self.rightSmallButton.setChecked(False)
    #     self.rightLargeButton.setText('\u2BC8\u2BC8')
    #     self.rightLargeButton.setChecked(False)
    #     self.leftLarge.setText('<--')
    #     self.leftLarge.setChecked(False)
    #     self.leftSmall.setText('<-')
    #     self.leftSmall.setChecked(False)
    #     self.rightLarge.setText('-->')
    #     self.rightLarge.setChecked(False)
    #     self.rightSmall.setText('->')
    #     self.rightSmall.setChecked(False)
    #     self.posInput.setMinimum(0.000)
    #     self.posInput.setMaximum(25.000)
    #     self.posInput.singleStep()

    #     self.tirGoButton.setChecked(False)

    #     if self.have_parent:
    #         self.ui.okButton.setText("Close")
    #         self.connect(self.ui.okButton, QtCore.SIGNAL(
    #             "clicked()"), self.handleOk)
    #     else:
    #         self.okButton.setText("Quit")
    #         self.okButton.clicked.connect(self.handleQuit)

    #     self.EPIButton.clicked.connect(self.goToEPI)
    #     self.TIRFButton.clicked.connect(self.goToTIRF)
    #     self.move_timer.timeout.connect(self.updatePosition)
    #     self.posInput.valueChanged.connect(self.updatePosition)
    #     self.leftSmallButton.clicked.connect(self.smallLeft)
    #     self.rightSmallButton.clicked.connect(self.smallRight)
    #     self.leftLargeButton.clicked.connect(self.largeLeft)
    #     self.rightLargeButton.clicked.connect(self.largeRight)
    #     self.tirGoButton.clicked.connect(self.goToX)
    #     self.rightLarge.clicked.connect(self.largeRightSmall)
    #     self.leftSmall.clicked.connect(self.smallLeftSmall)
    #     self.rightSmall.clicked.connect(self.smallRightSmall)
    #     self.leftLarge.clicked.connect(self.largeLeftSmall)

    #     grid.addWidget(self.EPIButton, 0, 0)
    #     grid.addWidget(self.leftLargeButton, 0, 1)
    #     grid.addWidget(self.leftSmallButton, 0, 2)
    #     grid.addWidget(self.rightSmallButton, 0, 3)
    #     grid.addWidget(self.rightLargeButton, 0, 4)
    #     grid.addWidget(self.TIRFButton, 0, 5)
    #     grid.addWidget(self.positionDisplay, 0, 6)
    #     grid.addWidget(self.leftLarge, 1, 1)
    #     grid.addWidget(self.leftSmall, 1, 2)
    #     grid.addWidget(self.rightSmall, 1, 3)
    #     grid.addWidget(self.rightLarge, 1, 4)
    #     grid.addWidget(self.posInput, 3, 5)
    #     grid.addWidget(self.tirGoButton, 3, 6)

   
    #     grid.addWidget(self.okButton, 4, 6)
    #     groupBox.setLayout(grid)


    def goToEPI(self):
        if self.debug:
            print("goToEPI")
        # self.moveStage(self.epi_position)

        self.position = self.epi_position
        self.moveStage()

    def goToTIRF(self):
        if self.debug:
            print("goToTIRF")
        self.position = self.tirf_position
        self.moveStage()
        # self.moveStage(self.tirf_position)

    def goToX(self):
        if self.debug:
            print("goToX")
        self.position = self.posInput.value()
        self.moveStage()

    def handleOk(self):
        if self.debug:
            print(" handleOk")
        self.hide()

    def handleQuit(self):
        if self.debug:
            print(" handleQuit")
        self.close()

    def largeLeft(self):
        if self.debug:
            print(" largeLeft")
        if self.position > 14.0:
            self.position -= 10.0 * self.jog_size
            self.moveStage()

    def largeRight(self):
        if self.debug:
            print(" largeRight")
        if self.position < 23.0:
            self.position += 10.0 * self.jog_size
            self.moveStage()

    def largeLeftSmall(self):
        if self.debug:
            print(" largeLeft")
        if self.position > 14.0:
            self.position -= 10.0 * self.jog_size_small
            self.moveStage()

    def largeRightSmall(self):
        if self.debug:
            print(" largeRight")
        if self.position < 23.0:
            self.position += 10.0 * self.jog_size_small
            self.moveStage()

    # def moveStage(self, pos):
    def moveStage(self):
        self.move_timer.start()
        self.smc100.stopMove()
        self.smc100.moveTo(self.position)
        self.setPositionText()

    def newParameters(self, parameters):
        if self.debug:
            print(" newParameters")
        self.debug = parameters.debug
        self.epi_position = parameters.epi_position
        self.tirf_position = parameters.tirf_position

        self.jog_size = parameters.jog_size


    def smallLeft(self):
        if self.debug:
            print(" smallLeft")
        if self.position > 14.0:
            self.position -= self.jog_size
            self.moveStage()

    def smallRight(self):
        if self.debug:
            print(" smallRight")
        if self.position < 23.0:
            self.position += self.jog_size
            self.moveStage()

    def smallLeftSmall(self):
        if self.debug:
            print(" smallLeft")
        if self.position > 14.0:
            self.position -= self.jog_size_small
            self.moveStage()

    def smallRightSmall(self):
        if self.debug:
            print(" smallRight")
        if self.position < 23.0:
            self.position += self.jog_size_small
            self.moveStage()

    def setPositionText(self):
        self.positionDisplay.setText("{0:.3f}".format(self.position))


    def updatePosition(self):
        if self.debug:
            print("updatePosition")
        if not self.smc100.amMoving():
            self.move_timer.stop()
        self.position = self.smc100.getPosition()
        self.setPositionText()

    def quit(self):
        if self.debug:
            print("quit (misc)")

      # self.position = self.epi_position
      # self.moveStage()

      # while self.smc100.amHoming():
      #     time.sleep(1)
        pass

    # def arKrChange(self, value):
    #     if self.debug:
    #         print ("arKrChange")
    #     self.arkrpower = value
    #     self.ui.arKrAmps.setText("{0:.1f} Amps".format(self.arkrpower))
    #     self.ui.arKrButton.show()

    # def changeArKrPower(self):
    #     if self.debug:
    #         print ("changeArKrPower")
    #     self.innova.setLaserCurrent(self.arkrpower)
    #     self.ui.arKrButton.hide()

    # def changedYAGPower(self):
    #     if self.debug:
    #         print ("changeYAGPower")
    #     if (self.old_dYAG_power != self.dYAG_power):
    #         self.compass.setPower(self.dYAG_power/self.dYAG_max)
    #         self.old_dYAG_power = self.dYAG_power
    #     self.ui.dYAGButton.hide()

    # def dYAGChange(self, value):
    #     if self.debug:
    #         print ("dYAGChange")
    #     self.dYAG_power = (float(value)/float(self.ui.dYAGSlider.maximum())) * self.dYAG_max
    #     self.ui.dYAGText.setText(str(self.dYAG_power) + " mw")
    #     self.ui.dYAGButton.show()

#
# testing
#


if __name__ == "__main__":
    app = QApplication(sys.argv)
    s = QStyleFactory.create('Fusion')  # Fusion is a button style
    app.setStyle(s)
    miscControl = MiscControl(0)
    miscControl.show()
    app.exec_()


#
# The MIT License
#
# Copyright (c) 2009 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
