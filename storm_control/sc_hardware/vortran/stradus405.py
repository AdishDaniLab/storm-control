#!/usr/bin/python
#
## @file
#
# Vortran stradus 405 laser control.
#
# Hazen 7/10 (com port modified Josh 6/26/13)
#

import stradus

## Stradus405
#
# Controls a Vortran stradus 405 laser. This is sub-class of stradus.Stradus.
#
class Stradus405(stradus.Stradus):

    ## __init__
    #
    # Initiate RS-232 communication, verify that the laser is responding.
    #
    # @param port (Optional) A string that specifies the port, the default is "COM13".
    #
    def __init__(self, port = "COM15"):
        stradus.Stradus.__init__(self, port)

#
# Testing
#

if __name__ == "__main__":
    stradus = Stradus405(port = "COM15")
    if stradus.getStatus():
        print stradus.getPowerRange()
        print stradus.getLaserOnOff()
        stradus.shutDown()

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

