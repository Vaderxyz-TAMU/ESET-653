import pyvisa as pyv
import numpy as np
import time
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
scope.configure_channel(1,7.5,1.0,'DC',1)
scope.configure_channel(2,7.5,-3,'DC',1)
scope.configure_timebase(1e-3)
scope.write_command('HOR:DEL:MOD ON')
scope.write_command('HOR:DEL:TIM 0.001')

#parameter collection
time.sleep(1.5) # Allow scope to acquire data

# Run the consolidated measurement function
# Assuming CH1 is input and CH2 is output
params = scope.measure_switching_parameters(1, 2)
print("5V VIN, 5 V VBias, 5 V VON")
if params:
    print(f"Channel 2 tON:    {(params['tON'] * 1e6):.3f} us")
    print(f"Channel 2 tRise:  {(params['tRise'] * 1e6):.3f} us")
    print(f"Channel 2 tDelay: {(params['tDelay'] * 1e6):.3f} us")
    print(f"Channel 2 tOFF:   {(params['tOFF'] * 1e6):.3f} us")
    print(f"Channel 2 tFall:  {(params['tFall'] * 1e6):.3f} us")

#-----0.8 VIn 5 V VBias, VOn ---------------------------------------------
psu.set_voltage(1, 0.8)
scope.configure_channel(1,.75,1.0,'DC',1)
scope.configure_channel(2,.75,-1,'DC',1)
scope.configure_timebase(1e-3)
scope.write_command('HOR:DEL:MOD ON')
scope.write_command('HOR:DEL:TIM 0.001')

time.sleep(2)

params = scope.measure_switching_parameters(1, 2)

print("\n0.8V VIN, 5 V VBias, 5 V VON")
if params:
    print(f"Channel 2 tON:    {(params['tON'] * 1e6):.3f} us")
    print(f"Channel 2 tRise:  {(params['tRise'] * 1e6):.3f} us")
    print(f"Channel 2 tDelay: {(params['tDelay'] * 1e6):.3f} us")
    print(f"Channel 2 tOFF:   {(params['tOFF'] * 1e6):.3f} us")
    print(f"Channel 2 tFall:  {(params['tFall'] * 1e6):.3f} us")

awg.set_output(1,0)
awg.set_output(2,0)
psu.output_off()