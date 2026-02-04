from bench.base_scpi import SCPIDevice

class AgilentE363x(SCPIDevice):
    """
    Robust Driver for Agilent/Keysight E3631A Triple Output PSU.
    Channels: P6V (+6V), P25V (+25V), N25V (-25V)
    """
    
    def __init__(self, inst):
        super().__init__(inst)
        # Default safety limits
        self.limit_volt = 30.0
        self.limit_curr = 3.0

    def set_safety_limits(self, max_voltage, max_current):
        """
        Set the maximum allowable values for this session.
        """
        self.limit_volt = abs(max_voltage)
        self.limit_curr = abs(max_current)
        print(f"Safety Limits Updated: Max {self.limit_volt}V, Max {self.limit_curr}A")

    def select_output(self, output):
        """
        Selects the active channel to adjust.
        Options: 'P6V', 'P25V', 'N25V'
        """
        output = output.upper()
        if output not in ['P6V', 'P25V', 'N25V']:
            raise ValueError(f"Invalid Output: {output}. Use P6V, P25V, or N25V.")
        self.write(f"INST:SEL {output}")

    def set_voltage(self, voltage, channel=None):
        """
        Sets voltage. If channel is provided, it selects it first.
        Example: psu.set_voltage(5.0, channel='P6V')
        """
        if channel:
            self.select_output(channel)
        
        # Safety Check
        if abs(voltage) > self.limit_volt:
            raise ValueError(f"SAFETY TRIP: {voltage}V exceeds limit of {self.limit_volt}V")
        
        self.write(f"VOLT {voltage}")

    def set_current(self, current, channel=None):
        """
        Sets current limit.
        """
        if channel:
            self.select_output(channel)

        if abs(current) > self.limit_curr:
            raise ValueError(f"SAFETY TRIP: {current}A exceeds limit of {self.limit_curr}A")
        
        self.write(f"CURR {current}")

    def measure_voltage(self, channel="P6V"):
        """
        Measures actual voltage output of a specific channel.
        """
        return float(self.query(f"MEAS:VOLT:DC? {channel}"))

    def measure_current(self, channel="P6V"):
        """
        Measures actual current draw of a specific channel.
        """
        return float(self.query(f"MEAS:CURR:DC? {channel}"))

    def output_on(self):
        """Enable output (All channels)."""
        self.write("OUTP ON")

    def output_off(self):
        """Disable output (All channels)."""
        self.write("OUTP OFF")