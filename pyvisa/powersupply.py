import pyvisa

# Windows: Use NI-VISA backend
rm = pyvisa.ResourceManager()
# Or specify DLL path explicitly
# rm = pyvisa.ResourceManager("C:/Windows/System32/visa32.dll")

instruments = rm.list_resources()
print(f"Found instruments: {instruments}")

# Open connection to first instrument
if instruments:
    inst = rm.open_resource(instruments[0])
    device_info = inst.query("*IDN?")
    print(f"Connected to: {device_info}")
    inst.close()


# Connect to power supply  
psu = rm.open_resource("GPIB0::3::INSTR")

# Configure output
psu.write("VOLT 5.0")    # Set 12V
# psu.write("CURR 2.0")     # Limit to 2A  
psu.write("OUTP ON")      # Enable output

# Monitor load
voltage = float(psu.query("MEAS:VOLT?"))
current = float(psu.query("MEAS:CURR?"))
power = voltage * current

print(f"Load: {voltage:.2f}V, {current:.3f}A, {power:.2f}W")

rm.close()