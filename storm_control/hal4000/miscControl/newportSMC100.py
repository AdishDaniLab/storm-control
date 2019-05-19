#!/usr/bin/python
#
# @file
#
# GUI for the Newport SMC100 motor controller, with EPI/TIRF options.
#
# Hazen 1/10 (Modified by Gayatri 5/19)
#

import sys

import storm_control.sc_library.parameters as params

import storm_control.hal4000.halLib.halDialog as halDialog
import storm_control.hal4000.halLib.halMessage as halMessage
import storm_control.hal4000.halLib.halModule as halModule

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
import storm_control.sc_hardware.newport.smc100 as SMC100

#
# Misc Control Dialog Box
#


class NewportControl(halDialog.HalDialog):
    def __init__(self, configuration = None, **kwds):
        super().__init__(**kwds)
        # QMainWindow.__init__(self, parent)
        self.parameters = params.StormXMLObject()
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
            self.okButton.clicked.connect(self.handleOk)
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

####################################################################################################

        # set modeless
        self.setModal(False)
        self.home_position = 0.0
        self.epi_position = 17.2
        self.tirf_position = 19.9
        self.jog_size = 0.05

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

        # Build the GUI layout here.

        self.EPIButton = QToolButton()
        self.TIRFButton = QToolButton()
        self.leftLargeButton = QToolButton()
        self.leftSmallButton = QToolButton()
        self.rightSmallButton = QToolButton()
        self.rightLargeButton = QToolButton()
        self.okButton = QPushButton('Quit', self)
        self.positionDisplay = QLabel()
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
        self.posInput.setMinimum(0.000)
        self.posInput.setMaximum(25.000)
        self.posInput.singleStep()

        self.tirGoButton.setChecked(False)
        

        grid = QGridLayout()
        grid.addWidget(self.EPIButton, 0, 0)
        grid.addWidget(self.leftLargeButton, 0, 1)
        grid.addWidget(self.leftSmallButton, 0, 2)
        grid.addWidget(self.rightSmallButton, 0, 3)
        grid.addWidget(self.rightLargeButton, 0, 4)
        grid.addWidget(self.TIRFButton, 0, 5)
        grid.addWidget(self.positionDisplay, 0, 6)
        grid.addWidget(self.posInput, 3, 5)
        grid.addWidget(self.tirGoButton, 3, 6)
        grid.addWidget(self.okButton, 4, 6)
        self.setLayout(grid)

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
class NewportSMC100(halModule.HalModule):

    def __init__(self, module_params = None, qt_settings = None, **kwds):
        super().__init__(**kwds)
        self.configuration = module_params.get("configuration")

        self.view = ZStageView(module_name = self.module_name,
                               configuration = module_params.get("configuration"))
        self.view.halDialogInit(qt_settings,
                                module_params.get("setup_name") + " z stage")

    def cleanUp(self, qt_settings):
        self.view.cleanUp(qt_settings)

    def handleResponse(self, message, response):
        if message.isType("get functionality"):
            self.view.setFunctionality(response.getData()["functionality"])

    def processMessage(self, message):

        if message.isType("configure1"):
            self.sendMessage(halMessage.HalMessage(m_type = "add to menu",
                                                   data = {"item name" : "Z Stage",
                                                           "item data" : "z stage"}))

            self.sendMessage(halMessage.HalMessage(m_type = "get functionality",
                                                   data = {"name" : self.configuration.get("z_stage_fn")}))

            self.sendMessage(halMessage.HalMessage(m_type = "initial parameters",
                                                   data = {"parameters" : self.view.getParameters()}))            

        elif message.isType("new parameters"):
            p = message.getData()["parameters"]
            message.addResponse(halMessage.HalMessageResponse(source = self.module_name,
                                                              data = {"old parameters" : self.view.getParameters().copy()}))
            self.view.newParameters(p.get(self.module_name))
            message.addResponse(halMessage.HalMessageResponse(source = self.module_name,
                                                              data = {"new parameters" : self.view.getParameters()}))

        elif message.isType("show"):
            if (message.getData()["show"] == "z stage"):
                self.view.show()

        elif message.isType("start"):
            if message.getData()["show_gui"]:
                self.view.showIfVisible()


#
# testing
#


if __name__ == "__main__":
    app = QApplication(sys.argv)
    s = QStyleFactory.create('Fusion')  # Fusion is a button style
    app.setStyle(s)
    newportControl = NewportControl(0)
    newportControl.show()
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
