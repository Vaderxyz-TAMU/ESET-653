import pyvisa
import time

class PSU:
    def __init__(self, resource_string):
        self.rm = pyvisa.ResourceManager()
        self.psu = self.rm.open_resource(resource_string)

        # Configure timeout and termination characters
        self.psu.read_termination = '\n'
        self.psu.write_termination = '\n'

        # Verify and Initialize
        self.psu.write("*CLS")
        idn = self.psu.query("*IDN?")
        print(f"Connected to: {idn.strip()}")

    def _resolve_channel(self, channel):
        """
        Helper to map integer inputs to SCPI string identifiers.
        1 -> P6V
        2 -> P25V
        3 -> N25V
        Also accepts the strings directly if passed.
        """
        # Mapping based on Output Identifiers table 
        chan_map = {1: 'P6V', 2: 'P25V', 3: 'N25V'}
        
        if channel in chan_map:
            return chan_map[channel]
        elif str(channel).upper() in chan_map.values():
            return str(channel).upper()
        else:
            raise ValueError("Channel must be 1 (P6V), 2 (P25V), or 3 (N25V)")

    # --- Output Configuration ---

    def apply(self, channel, voltage, current=None):
        """
        Uses the APPLy command to set voltage and current in one go.
        Channel inputs:
        1 -> +6V
        2 -> +25V
        3 -> -25V
        """
        scpi_chan = self._resolve_channel(channel)
        
        if current is not None:
            self.psu.write(f"APPL {scpi_chan}, {voltage}, {current}")
        else:
            self.psu.write(f"APPL {scpi_chan}, {voltage}")

    def select_channel(self, channel):
        """Selects the output channel"""
        scpi_chan = self._resolve_channel(channel)
        self.psu.write(f"INST:SEL {scpi_chan}")

    def set_voltage(self, channel, volts):
        """Sets immediate voltage for a specific channel."""
        self.select_channel(channel)
        self.psu.write(f"VOLT {volts}")

    def set_current(self, channel, amps):
        """Sets immediate current limit for a specific channel"""
        self.select_channel(channel)
        self.psu.write(f"CURR {amps}")

    def set_trigger_levels(self, channel, volts, amps):
        """Sets the voltage/current levels that will activate on a trigger"""
        self.select_channel(channel)
        self.psu.write(f"VOLT:TRIG {volts}")
        self.psu.write(f"CURR:TRIG {amps}")

    # --- Output Control ---

    def output_on(self):
        """Enables the output"""
        self.psu.write("OUTP ON")

    def output_off(self):
        """Disables the output"""
        self.psu.write("OUTP OFF")
    
    def tracking_on(self):
        """Enables tracking mode for +25V and -25V supplies"""
        self.psu.write("OUTP:TRAC ON")

    def tracking_off(self):
        """Disables tracking mode"""
        self.psu.write("OUTP:TRAC OFF")

    # --- Measurement ---

    def measure_voltage(self, channel=None):
        """Queries the actual voltage at the terminals"""
        cmd = "MEAS:VOLT?"
        if channel:
            cmd += f" {self._resolve_channel(channel)}"
        return float(self.psu.query(cmd))

    def measure_current(self, channel=None):
        """Queries the actual current at the terminals"""
        cmd = "MEAS:CURR?"
        if channel:
            cmd += f" {self._resolve_channel(channel)}"
        return float(self.psu.query(cmd))

    # --- System & Triggering ---

    def trigger(self):
        """Sends a bus trigger (*TRG)"""
        self.psu.write("*TRG")

    def initiate(self):
        """Initiates the trigger system"""
        self.psu.write("INIT")

    def beep(self):
        """Issues a single beep"""
        self.psu.write("SYST:BEEP")

    def get_error(self):
        """Reads the next error from the queue"""
        return self.psu.query("SYST:ERR?").strip()

    def reset(self):
        """Resets the instrument to default power-on state"""
        self.psu.write("*RST")

    def save_state(self, location):
        """Saves current state to memory location 1, 2, or 3"""
        if location in [1, 2, 3]:
            self.psu.write(f"*SAV {location}")
        else:
            print("Save location must be 1, 2, or 3")

    def recall_state(self, location):
        """Recalls state from memory location 1, 2, or 3"""
        if location in [1, 2, 3]:
            self.psu.write(f"*RCL {location}")
        else:
            print("Recall location must be 1, 2, or 3")

    def close(self):
        """Closes the connection"""
        self.psu.close()
        self.rm.close()