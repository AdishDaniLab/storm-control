#!/usr/bin/env python
"""
Thorlabs FW103S control.

Gayatri 4/19 
"""
import traceback
import storm_control.sc_hardware.baseClasses.illuminationHardware as illuminationHardware
from storm_control.sc_hardware.thorlabs.PyAPT.PyAPT import APTMotor
import time


class FW103S():
    """
    Encapsulates communication with a Thorlabs filter wheel through the APT dll.
    """

    def __init__(self, serialno):
        super().__init__()
        # Initializing motors

        print("fw103s : Initializing motors...")
        try:
            print("self.Motor = APTMotor(80831436, HWTYPE=29)")
            # self.Motor2 = APTMotor(80831430, HWTYPE=29)
            # self.Motor3 = APTMotor(80831429, HWTYPE=29)
            # self.Motor4 = APTMotor(80828888, HWTYPE=29)

            print("self.Motor.initializeHardwareDevice()")
            # self.Motor2.initializeHardwareDevice()
            # self.Motor3.initializeHardwareDevice()
            # self.Motor4.initializeHardwareDevice()
            print("fw103s : Initialized all hardware")
            time.sleep(.1)
        except:

            print(traceback.format_exc())
            print("Failed to connect to FW103S filter wheels !")

    def setPosition(self, position):
        """
        Moves filter wheel to indicated ND filter's position.
        """
        print("self.Motor.mAbs(position)")
        time.sleep(.1)

    def getPosition(self):
        """
        Requests filter wheel position information.
        """
        print("pos = self.Motor.getPos()")
        return pos

    def shutDown(self):
        print("self.Motor.cleanUpAPT()")
        print("Stepper motor disconnected! ")


if (__name__ == "__main__"):
    fwheel = FW103S()
    fwheel.shutDown()

#
# The MIT License
#
# Copyright (c) 2012 Zhuang Lab, Harvard University
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
