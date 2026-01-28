from bench.base_scpi import SCPIDevice

class Agilent34401A(SCPIDevice):
    def configure_dc_voltage(self, range=10, resolution=0.001):
        self.write(f"CONF:VOLT:DC {range},{resolution}")

    def read_voltage(self):
        return float(self.query("READ?"))

    def measure_voltage(self):
        return float(self.query("MEAS:VOLT:DC?"))
