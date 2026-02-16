import pyvisa as pyv
import numpy as np
import time
import matplotlib.pyplot as plt
from instruments.PSU import *
from instruments.DMM import *
from instruments.AWG import *
from instruments.OSCOPE import *

# awg = AWG("USB0::0xF4EC::0xEE38::574C20107::INSTR")
# psu = PSU("GPIB0::3::INSTR")
# dmm = DMM("GPIB0::20::INSTR")
scope = OSCOPE("USB0::0x0699::0x0378::C011758::INSTR")

# awg.set_sine_wave(1000,1,2.5,1)
# awg.enable_output()

# psu.beep()
# psu.apply(1,5.0)
# psu.output_on

# dmm.measure_current_dc()

scope.save_screenshot()
