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
        
        # Step 1: Apply power
        psu = self.instruments['power_supply']
        psu.write("VOLT 5.0")
        psu.write("CURR 1.0") 
        psu.write("OUTP ON")
        time.sleep(1)  # Settling time
        
        # Step 2: Generate test signal
        sig_gen = self.instruments['signal_generator']
        sig_gen.write("SOUR:FUNC SIN")
        sig_gen.write("SOUR:FREQ 1000")
        sig_gen.write("SOUR:VOLT 1.0")
        sig_gen.write("OUTP ON")
        time.sleep(0.5)
        
        # Step 3: Measure response
        scope = self.instruments['oscilloscope']
        scope.write("SING")
        scope.query("*OPC?")
        
        frequency = float(scope.query("MEASU:FREQ?"))
        amplitude = float(scope.query("MEASU:PK2PK?"))
        
        # Step 4: Measure power consumption
        supply_voltage = float(psu.query("MEAS:VOLT?"))
        supply_current = float(psu.query("MEAS:CURR?"))
        power_consumption = supply_voltage * supply_current
        
        # Step 5: Cleanup
        sig_gen.write("OUTP OFF")
        psu.write("OUTP OFF")
        
        results = {
            'input_frequency': 1000,
            'output_frequency': frequency,
            'output_amplitude': amplitude,
            'power_consumption': power_consumption,
            'test_passed': abs(frequency - 1000) < 10  # 10 Hz tolerance
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

# Example usage
controller = TestSequenceController()
controller.add_instrument('power_supply', 'ASRL/dev/ttyUSB0::INSTR', 
                         timeout=5000, termination='\n')
controller.add_instrument('signal_generator', 'USB0::0x2A8D::0x0001::MY52345678::INSTR')
controller.add_instrument('oscilloscope', 'USB0::0x0699::0x0363::C065089::INSTR')

# Run test sequence
test_results = controller.device_under_test_sequence()
print(f"Test results: {test_results}")

controller.close_all()