from bench.base_scpi import SCPIDevice
import time

class Agilent34401A(SCPIDevice):
    """
    Robust Driver for Agilent/Keysight 34401A / 34410A DMM.
    """

    def set_text(self, text):
        """Displays a message on the DMM screen."""
        self.write(f'DISP:TEXT "{text}"')

    def clear_text(self):
        """Clears the message and returns to normal display."""
        self.write("DISP:TEXT:CLE")

    # --- Configuration Methods (Setup Mode) ---
    
    def configure_voltage_dc(self, range_val="AUTO", resolution="DEF"):
        """
        Configures DC Voltage measurement.
        range_val: 'AUTO', 0.1, 1, 10, 100, 1000
        """
        self.write(f"CONF:VOLT:DC {range_val},{resolution}")

    def configure_voltage_ac(self, range_val="AUTO", resolution="DEF"):
        self.write(f"CONF:VOLT:AC {range_val},{resolution}")

    def configure_current_dc(self, range_val="AUTO", resolution="DEF"):
        self.write(f"CONF:CURR:DC {range_val},{resolution}")

    def configure_resistance(self, wires=2, range_val="AUTO", resolution="DEF"):
        """
        wires: 2 for standard leads, 4 for Kelvin (4-wire) measurement.
        """
        mode = "RES" if wires == 2 else "FRES"
        self.write(f"CONF:{mode} {range_val},{resolution}")

    def set_high_impedance(self, enable=True):
        """
        CRITICAL: Enables >10 GigOhm input resistance for 10V range and below.
        Prevents the DMM from loading down sensitive circuits.
        """
        state = "ON" if enable else "OFF"
        self.write(f"INP:IMP:AUTO {state}")

    # --- Measurement Methods ---

    def read_value(self):
        """
        Reads the value based on the current configuration.
        Fastest method if you are looping.
        """
        return float(self.query("READ?"))

    def measure_voltage(self):
        """Auto-configures and reads DC Voltage (Convenience method)."""
        return float(self.query("MEAS:VOLT:DC?"))

    def measure_current(self):
        """Auto-configures and reads DC Current."""
        return float(self.query("MEAS:CURR:DC?"))

    def measure_resistance(self):
        """Auto-configures and reads 2-Wire Resistance."""
        return float(self.query("MEAS:RES?"))