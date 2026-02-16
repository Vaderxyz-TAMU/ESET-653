import pyvisa as pyv
import numpy as np
import time
import matplotlib.pyplot as plt
from instruments.PSU import *
from instruments.DMM import *
from instruments.AWG import *
from instruments.OSCOPE import *

# # USB0::0xF4EC::0xEE38::574C20107::INSTR' -AWG
# # USB0::0x0699::0x0378::C011758::INSTR - OScope
# # ASRL1::INSTR - Unknown
# # ASRL3::INSTR - Unknown
# # GPIB0::3::INSTR - PSU
# # GPIB0::20::INSTR - DMM

scope = OSCOPE("USB0::0x0699::0x0378::C011758::INSTR")
awg = AWG("USB0::0xF4EC::0xEE38::574C20107::INSTR")
psu = PSU("GPIB0::3::INSTR")
# dmm = DMM("GPIB0::20::INSTR")


#PSU Setup
psu.set_voltage(1, 5.0)
psu.set_voltage(2,5.0)
psu.set_current(1,0.4)
psu.set_current(2,0.1)
psu.output_on()

#AWG Setup
awg.set_square_wave(50,2.0,0,25,1)
awg.set_square_wave(50,2.0,0,25,2)
awg.set_output(1,1)
awg.set_output(2,1)

# Oscilloscope Setup
scope.configure_channel(1,7.5,-2.0,'DC',1)
scope.configure_channel(2,7.5,-4,'DC',1)
scope.configure_timebase(1e-3)
scope.write_command('HOR:DEL:MOD ON')
scope.write_command('HOR:DEL:TIM 0.001')

results = scope.calculate_waveform_parameters('CH1','CH2')

for key, value in results.items():
    print(f"{key}: {(float(value) * pow(10,6)):.3f} us")

time.sleep(5)

awg.set_output(1,0)
awg.set_output(2,0)
psu.output_off()

# psu.close()
# awg.close()
# dmm.close()