#!/usr/bin/env python
"""
HAL module for controlling a Thorlabs filter wheel.

Hazen 04/18
"""

import storm_control.hal4000.halLib.halMessage as halMessage

import storm_control.sc_hardware.baseClasses.amplitudeModule as amplitudeModule
import storm_control.sc_hardware.thorlabs.FW103S as FW103S


# FIXME: Should be amplitudeModule.AmplitudeFunctionalityBuffered?
#
class FW103SFilterWheelFunctionality(amplitudeModule.AmplitudeFunctionality):

    def __init__(self, filter_wheel = None, **kwds):
        super().__init__(**kwds)
        self.filter_wheel = filter_wheel
        #self.on = True

    def onOff(self, power, state):
        pass
    
    def output(self, power):
        self.filter_wheel.setPosition(power)


class FW103SFilterWheelModule(amplitudeModule.AmplitudeModule):

    def __init__(self, module_params = None, qt_settings = None, **kwds):
        super().__init__(**kwds)
        self.filter_wheel_functionality = None

        configuration = module_params.get("configuration")
        filter_wheel = FW103S.FW103S(wavelength = configuration.get("wavelength"))
                                    

        if filter_wheel.getStatus():
            self.filter_wheel_functionality = FW103SFilterWheelFunctionality(display_normalized = False,
                                                                             filter_wheel = filter_wheel,
                                                                             maximum = configuration.get("maximum"),
                                                                             used_during_filming = False)
        
        
    def getFunctionality(self, message):
        if (message.getData()["name"] == self.module_name):
            if self.filter_wheel_functionality is not None:
                message.addResponse(halMessage.HalMessageResponse(source = self.module_name,
                                                                  data = {"functionality" : self.filter_wheel_functionality}))
            
