#!/usr/bin/env python
"""
Vortran Stradus laser control (via RS-232)

Gayatri 5/19
"""
import traceback
import storm_control.sc_hardware.serial.RS232 as RS232

class Stradus(RS232.RS232):
    """
    This class controls a Vortran Stradus laser using RS-232 communication.
    """
    def __init__(self, **kwds):
        """
        Connect to the laser by RS-232 and verify that the connection has been made.
        """
        # Add Stradus RS232 default settings.
        kwds["baudrate"] = 19200
        # kwds["end_of_line"] = "\r"
        kwds["wait_time"] = 0.05
        # kwds["timeout"] = None
        self.on = False
        self.pmin = 0.0
        self.pmax = 5.0

        try:
            # open port
            super().__init__(**kwds)

            # see if the laser is connected
            assert not(self.commWithResp("?HID") == None)

        # FIXME: This should not catch everything!
        except Exception:
            print(traceback.format_exc())
            self.live = False
            print("Failed to connect to Stradus Laser at port", kwds["port"])
            print("Perhaps it is turned off or the COM ports have")
            print("been scrambled?")

        if self.live:
            [self.pmin, self.pmax] = self.getPowerRange()
            self.setExtControl(False)
            if (not self.getLaserOnOff()):
                self.setLaserOnOff(True)
                self.setPower(001.0)

    def respToFloat(self, resp):
        """
        Convert a response from the laser to a floating point number.
        """
        return float(resp.rsplit("=", 1)[1][:-12])

    def getExtControl(self):
        """
        Checks if the laser is configured for external control.
        """
        self.sendCommand("?EPC")
        response = self.waitResponse(end_of_response = '\r\nStradus:')

        # I don't know if end_of_response = '\r\nStradus:' has any effect on output.
        # Anyway , let it be.

        if (response.rsplit("=", 1)[1][:-13] == '0'):
            return False
        else:
            return True

    def getLaserOnOff(self):
        """
        Checks if the laser is on or off.
        """
        self.sendCommand("?LE")
        resp = self.waitResponse(end_of_response = '\r\nStradus:')
        if (resp.rsplit("=", 1)[1][:-12] == "1"):
            self.on = True
            return True
        else:
            self.on = False
            return False

    def getPowerRange(self):
        """
        Returns the laser power range (in mW?).
        """
        # self.sendCommand("?MINLP")
        # print("?MINLP")
        # print("Minimum : ", self.waitResponse())
        # pmin1 = self.respToFloat(self.waitResponse(), 6)
        pmin = 001.0
        self.sendCommand("?MAXP")
        resp=self.waitResponse(end_of_response = '\r\nStradus:')
        pmax = self.respToFloat(resp)
        return [pmin, pmax]

    def getPower(self):
        """
        Return the current laser power (in mW?).
        """
        self.sendCommand("?LP")
        power_string = self.waitResponse()
        return float(power_string.rsplit("=", 1)[1][:-12])

    def setExtControl(self, mode):
        """
        Set the laser to external control mode.
        """
        if mode:
            self.sendCommand("EPC=1")
            self.waitResponse(end_of_response = '\r\nStradus:')
        else:
            self.sendCommand("EPC=0")
            self.waitResponse(end_of_response = '\r\nStradus:')

    def setLaserOnOff(self, on):
        """
        Turn the laser on or off.
        """
        if on and (not self.on):
            self.sendCommand("LE=1")
            self.waitResponse(end_of_response = '\r\nStradus:')
            self.on = True
        if (not on) and self.on:
            self.sendCommand("LE=0")
            self.waitResponse(end_of_response = '\r\nStradus:')
            self.on = False

    def setPower(self, power_in_mw):
        """
        Set the laser power (in mW).
        """
        if power_in_mw > self.pmax:
            power_in_mw = self.pmax
        power_in_mw = str(round(power_in_mw, 1)).zfill(5) 
        # 'zfill' is used to make command format LP=###.# (mW) as mentioned in the command reference.
        # For example, LP=10.05 may not work. But LP=010.1 will work. 
        # Also, the laser ignores the command if I try to set power as 000.0. Minimum power when laser
        # emission is enabled is 1.4 mW. I can get this by sending command LP=001.0 instead.
        if power_in_mw == '000.0' :
            power_in_mw = '001.0'
        self.sendCommand("LP=" + power_in_mw)
        self.waitResponse(end_of_response = '\r\nStradus:')

    def shutDown(self):
        """
        Turn the laser off & close the RS-232 connection.
        """
        if self.live:
            self.setLaserOnOff(False)
        super().shutDown()


#
# Testing
#
if (__name__ == "__main__"):
    stradus = Stradus(port="COM14")
    kapish = 'y'
    if stradus.getStatus():
        while(kapish == 'y'):
            instruction = input("Send : ")
            stradus.sendCommand(str(instruction))
            # time.sleep(0.5)
            response = stradus.waitResponse(end_of_response="\r\nStradus:")
            print(response)
            # print("Response : ", response.rsplit("=", 1)[1][:-1])
            # print("Power range : ", stradus.getPowerRange())
            kapish = input("Again ? (y/n) : ")

            
        stradus.shutDown()
    else:
        sys.exit()

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
