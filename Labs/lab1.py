import pyvisa
import time
import csv
from datetime import datetime

# USB0::0xF4EC::0xEE38::574C20107::INSTR' -AWG
# USB0::0x0699::0x0378::C011758::INSTR - OScope
# ASRL1::INSTR - Unknown
# ASRL3::INSTR - Unknown
# GPIB0::3::INSTR - PSU
# GPIB0::20::INSTR - DMM

class TestSequenceController:
    """Coordinate multiple instruments for complex tests"""
    
    def __init__(self):
        self.instruments = {}
        self.rm = pyvisa.ResourceManager()
    
    def add_instrument(self, name, resource_string, **config):
        """Add instrument to test setup"""
        inst = self.rm.open_resource(resource_string)
        
        # Apply configuration
        if 'timeout' in config:
            inst.timeout = config['timeout']
        if 'termination' in config:
            inst.write_termination = config['termination']
            inst.read_termination = config['termination']
        
        self.instruments[name] = inst
        print(f"Added {name}: {inst.query('*IDN?').strip()}")
    
    def device_under_test_sequence(self):
        """Example: Device characterization sequence"""
        
        # # Step 1: Apply power
        # psu = self.instruments['power_supply']
        # psu.write("VOLT 2.5")
        # psu.write("CURR 1.0") 
        # psu.write("OUTP ON")
        # time.sleep(1)  # Settling time
        
        # # Step 2: Generate test signal
        # sig_gen = self.instruments['signal_generator']
        # sig_gen.write("C1:BSWV WVTP,SINE")
        # sig_gen.write("C1:BSWV FRQ,1000")
        # sig_gen.write("C1:BSWV OFST,1.0")
        # sig_gen.write("C1:OUTP ON")
        # time.sleep(0.5)
        
        # Step 3: Measure response
        scope = self.instruments['oscilloscope']
        scope.write("*RST")
        scope.write("*CLS")
        
        scope.write("SELECT:CH1 ON")
        
        frequency = float(scope.query("MEASUREMENT:IMMED:VALUE?"))
        # amplitude = float(scope.query("MEASU:PK2PK?"))

        print(frequency)
        # print(amplitude)
        
        # # Step 4: Measure power consumption
        # supply_voltage = float(psu.query("MEAS:VOLT?"))
        # supply_current = float(psu.query("MEAS:CURR?"))
        # power_consumption = supply_voltage * supply_current
        
        # # Step 5: Cleanup
        # sig_gen.write("OUTP OFF")
        # psu.write("OUTP OFF")
        
        results = {
             'input_frequency': 1000,
             'output_frequency': frequency,
            # 'output_amplitude': amplitude,
            #  'power_consumption': power_consumption,
            #  'test_passed': abs(frequency - 1000) < 10  # 10 Hz tolerance
         }
        
        return results
    
    def close_all(self):
        """Clean up all instruments"""
        for name, inst in self.instruments.items():
            try:
                inst.close()
            except:
                pass
        self.rm.close()

# USB0::0xF4EC::0xEE38::574C20107::INSTR' -AWG
# USB0::0x0699::0x0378::C011758::INSTR - OScope
# ASRL1::INSTR - Unknown
# ASRL3::INSTR - Unknown
# GPIB0::3::INSTR - PSU
# GPIB0::20::INSTR - DMM

# Example usage
controller = TestSequenceController()
controller.add_instrument('power_supply', 'GPIB0::3::INSTR')
controller.add_instrument('signal_generator', 'USB0::0xF4EC::0xEE38::574C20107::INSTR')
controller.add_instrument('oscilloscope', 'USB0::0x0699::0x0378::C011758::INSTR')
controller.add_instrument('dmm', 'GPIB0::20::INSTR')
print(f"Connected Instruments: {controller.instruments}")

# Run test sequence
test_results = controller.device_under_test_sequence()
# print(f"Test Results: {test_results}")

controller.close_all()