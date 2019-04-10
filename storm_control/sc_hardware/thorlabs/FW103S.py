#!/usr/bin/env python
"""
Thorlabs FW103S control.

Gayatri 4/19 
"""
import traceback
import storm_control.sc_hardware.baseClasses.illuminationHardware as illuminationHardware
from PyAPT.PyAPT import APTMotor
import time

class FW103S():
    """
    Encapsulates communication with a Thorlabs filter wheel through the APT dll.
    """
    def __init__(self):
        super().__init__()
        # Initializing motors
        print("fw103s : Initializing motors...")
        try:
            self.Motor1 = APTMotor(80831436, HWTYPE=29)
            self.Motor2 = APTMotor(80831430, HWTYPE=29)
            self.Motor3 = APTMotor(80831429, HWTYPE=29)
            self.Motor4 = APTMotor(80828888, HWTYPE=29)

            self.Motor1.initializeHardwareDevice()
            self.Motor2.initializeHardwareDevice()
            self.Motor3.initializeHardwareDevice()
            self.Motor4.initializeHardwareDevice()
            print("fw103s : Initialized all hardware")
            time.sleep(.1)
        except:
            print(traceback.format_exc())
            print("Failed to connect to FW103S filter wheels !")

    def setPosition(self, wavelength):
        """
        Moves filter wheel to indicated ND filter's position.
        """
        nd = [['ND 0', 0.0], ['ND 0.5', 60.0], ['ND 1', 120.0],
              ['ND 1.3', 180.0], ['ND 2', 240.0], ['ND 3', 300]]
        for (ndval, pos) in nd:
            if ndval == self.sender().text():
                position = pos
            else:
                pass


