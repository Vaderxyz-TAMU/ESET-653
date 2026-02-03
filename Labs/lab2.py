import pyvisa
import time
import numpy as np
import csv

# USB0::0xF4EC::0xEE38::574C20107::INSTR' -AWG
# USB0::0x0699::0x0378::C011758::INSTR - OScope
# ASRL1::INSTR - Unknown
# ASRL3::INSTR - Unknown
# GPIB0::3::INSTR - PSU
# GPIB0::20::INSTR - DMM

#PSU Setup
psu.write("APPL CH1, 5.0, 1.0")

psu.write("OUTP ON")

#AWG Setup

awg.write("SOUR1:FUNC SQU; FREQ 50; VOLT 5.0;)
awg.write("SOUR1:FUNC:SQU:DCYC 50")

awg.write("SOUR2:FUNC SQU; FREQ 50; VOLT 5.0;)
awg.write("SOUR2:FUNC:SQU:DCYC 50")

awg.write("OUTP1 ON; OUTP2 ON")

# Oscilloscope Setup

oscope.write("TIM:SCAL 0.005")
oscope.write("RUN")

time.sleep(2.5)

oscope.write("STOP")

#tON

oscope.write("MEAS:DEF DEL, +1, +1")

ch_3_ton = oscope.query("MEAS:DEL? CH1, CH3")

ch_4_ton = oscope.query("MEAS:DEL? CH2, CH4")

print(f"Channel 3 tON: {(float(ch_3_ton) * pow(10,3)):.3f} ms")

print(f"Channel 4 tON: {(float(ch_4_ton) * pow(10,6)):.3f} ms")

print()

#tOFF

oscope.write("MEAS:DEF DEL, +1, +1")

ch_3_ton = oscope.query("MEAS:DEL? CH1, CH3")

ch_4_ton = oscope.query("MEAS:DEL? CH2, CH4")

print(f"Channel 3 tON: {(float(ch_3_ton) * pow(10,3)):.3f} ms")

print(f"Channel 4 tON: {(float(ch_4_ton) * pow(10,6)):.3f} ms")

print()

#tRise

oscope.write("MEAS:DEF DEL, +1, +1")

ch_3_ton = oscope.query("MEAS:DEL? CH1, CH3")

ch_4_ton = oscope.query("MEAS:DEL? CH2, CH4")

print(f"Channel 3 tON: {(float(ch_3_ton) * pow(10,3)):.3f} ms")

print(f"Channel 4 tON: {(float(ch_4_ton) * pow(10,6)):.3f} ms")

print()

#tFall

oscope.write("MEAS:DEF DEL, +1, +1")

ch_3_ton = oscope.query("MEAS:DEL? CH1, CH3")

ch_4_ton = oscope.query("MEAS:DEL? CH2, CH4")

print(f"Channel 3 tON: {(float(ch_3_ton) * pow(10,3)):.3f} ms")

print(f"Channel 4 tON: {(float(ch_4_ton) * pow(10,6)):.3f} ms")

print()

#tDelay

oscope.write("MEAS:DEF DEL, +1, +1")

oscope.write("MEAS:DEL? CH1, CH3")

oscope.write("MEAS:DEL? CH2, CH4")

oscope.write("RUN")

ascii_data_ch_1 = oscope.query("WAV:DATA? CH1")

data_ch_1 = 

ch_1_x1_inc = float(oscope.query("WAV:XINC?"))

ch_1_x1_origin = float(oscope.query("WAV:XOR?"))

time_ch_1 = 

# max_ch_3 = np.max(data_ch_1)

ind1 = 

# print(ch_1_fifty_time)

oscope.write("WAV:DATA? CH2")

oscope.write("WAV:XINC?")

oscope.write("WAV:XOR?")

oscope.write("RUN")

ascii_data_ch_3 = oscope.query("WAV:DATA? CH3")

data_ch_3 = np.array(ascii_data_ch_3.split(",")).astype(np.float)

ch_3_x2_inc = float(oscope.query("WAV:XINC?"))

ch_3_x2_origin = float(oscope.query("WAV:XOR?"))

time_ch_3 = 

# max2 = np.max(data2)

ind3 = 

ch_3_ten_time = time_ch_3[ind3]

# print(ch_3_ten_time)

oscope.write("WAV:DATA? CH4")

ch_3_t