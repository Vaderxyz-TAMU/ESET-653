import pyvisa
import time
import statistics

class DMM:
    def __init__(self, resource_string):
        self.rm = pyvisa.ResourceManager()
        self.dmm = self.rm.open_resource(resource_string)
        
        # Configure for optimal performance
        self.dmm.timeout = 10000
        self.dmm.write_termination = '\n'
        self.dmm.read_termination = '\n'
        
        # Verify connection
        idn = self.dmm.query("*IDN?")
        print(f"Connected to: {idn.strip()}")
        
        # Initialize to known state
        self.reset()
        self.clear_status()

    # ==========================================
    # Core IEEE-488 Commands
    # ==========================================
    def reset(self):
        """Reset the instrument to factory default state (*RST)."""
        self.dmm.write("*RST")

    def clear_status(self):
        """Clear status registers and error queue (*CLS)."""
        self.dmm.write("*CLS")

    def self_test(self):
        """Perform a self-test and return result (*TST?)."""
        return self.dmm.query("*TST?")

    def wait_for_complete(self):
        """Wait for all pending operations to complete (*OPC?)."""
        return self.dmm.query("*OPC?")

    # ==========================================
    # High-Level Measurements (MEASure?)
    # ==========================================
    # These commands preset settings, trigger, and return a reading immediately.
    
    def measure_voltage_dc(self, range_val='DEF', resolution='DEF'):
        return float(self.dmm.query(f"MEAS:VOLT:DC? {range_val},{resolution}"))

    def measure_voltage_ac(self, range_val='DEF', resolution='DEF'):
        return float(self.dmm.query(f"MEAS:VOLT:AC? {range_val},{resolution}"))

    def measure_current_dc(self, range_val='DEF', resolution='DEF'):
        return float(self.dmm.query(f"MEAS:CURR:DC? {range_val},{resolution}"))

    def measure_current_ac(self, range_val='DEF', resolution='DEF'):
        return float(self.dmm.query(f"MEAS:CURR:AC? {range_val},{resolution}"))

    def measure_resistance(self, range_val='DEF', resolution='DEF'):
        """2-Wire Resistance measurement"""
        return float(self.dmm.query(f"MEAS:RES? {range_val},{resolution}"))

    def measure_fresistance(self, range_val='DEF', resolution='DEF'):
        """4-Wire Resistance measurement"""
        return float(self.dmm.query(f"MEAS:FRES? {range_val},{resolution}"))

    def measure_frequency(self):
        return float(self.dmm.query("MEAS:FREQ?"))

    def measure_period(self):
        return float(self.dmm.query("MEAS:PER?"))

    # ==========================================
    # Configuration (CONFigure)
    # ==========================================
    # Presets configuration without triggering a reading immediately.
    
    def configure_voltage_dc(self, range_val='DEF', resolution='DEF'):
        self.dmm.write(f"CONF:VOLT:DC {range_val},{resolution}")

    def configure_voltage_ac(self, range_val='DEF', resolution='DEF'):
        self.dmm.write(f"CONF:VOLT:AC {range_val},{resolution}")

    def configure_current_dc(self, range_val='DEF', resolution='DEF'):
        self.dmm.write(f"CONF:CURR:DC {range_val},{resolution}")

    def configure_resistance(self, range_val='DEF', resolution='DEF'):
        self.dmm.write(f"CONF:RES {range_val},{resolution}")

    def configure_fresistance(self, range_val='DEF', resolution='DEF'):
        self.dmm.write(f"CONF:FRES {range_val},{resolution}")

    # ==========================================
    # Measurement Parameters (SENSe / INPut)
    # ==========================================
    
    def set_nplc(self, nplc, function="VOLT:DC"):
        """
        Set integration time in Number of Power Line Cycles.
        Valid values: 0.02, 0.2, 1, 10, 100.
        """
        self.dmm.write(f"{function}:NPLC {nplc}")

    def set_range(self, range_val, function="VOLT:DC"):
        """Set measurement range manually."""
        self.dmm.write(f"{function}:RANG {range_val}")

    def set_autorange(self, enable=True, function="VOLT:DC"):
        state = "ON" if enable else "OFF"
        self.dmm.write(f"{function}:RANG:AUTO {state}")

    def set_resolution(self, resolution, function="VOLT:DC"):
        """Set resolution (e.g., 0.000001 for 6.5 digits)."""
        self.dmm.write(f"{function}:RES {resolution}")

    def set_input_impedance_auto(self, enable=True):
        """
        OFF = Fixed 10M Ohm
        ON  = >10G Ohm for 100mV, 1V, 10V ranges (VOLT:DC only)
        """
        state = "ON" if enable else "OFF"
        self.dmm.write(f"INP:IMP:AUTO {state}")

    def set_autozero(self, mode="ON"):
        """Modes: OFF, ON, ONCE"""
        self.dmm.write(f"ZERO:AUTO {mode}")

    def set_ac_bandwidth(self, bandwidth):
        """Set AC filter. Options: 3 (slow), 20 (medium), 200 (fast) Hz."""
        self.dmm.write(f"DET:BAND {bandwidth}")

    # ==========================================
    # Triggering & Execution
    # ==========================================
    
    def set_trigger_source(self, source="IMM"):
        """Sources: IMMediate, EXTernal, BUS"""
        self.dmm.write(f"TRIG:SOUR {source}")

    def set_trigger_delay(self, seconds):
        """Set delay between trigger and measurement."""
        self.dmm.write(f"TRIG:DEL {seconds}")

    def set_trigger_count(self, count):
        """Number of triggers to accept before returning to idle."""
        self.dmm.write(f"TRIG:COUN {count}")

    def set_sample_count(self, count):
        """Number of readings to take per trigger."""
        self.dmm.write(f"SAMP:COUN {count}")

    def initiate(self):
        """Move from Idle to Wait-for-Trigger state."""
        self.dmm.write("INIT")

    def read(self):
        """Standard READ? query (Initiate + Fetch)."""
        return self.dmm.query("READ?")

    def fetch(self):
        """Retrieve readings from memory without re-triggering."""
        return self.dmm.query("FETCH?")

    def abort(self):
        """Abort current measurement and return to idle."""
        self.dmm.write("ABOR")

    def trigger(self):
        """Send software trigger (*TRG). Used when Source is BUS."""
        self.dmm.write("*TRG")

    # ==========================================
    # Math Subsystem (CALCulate)
    # ==========================================
    
    def math_enable(self, enable=True):
        state = "ON" if enable else "OFF"
        self.dmm.write(f"CALC:STAT {state}")

    def math_set_function(self, function):
        """Functions: NULL, DB, DBM, AVERage, LIMit"""
        self.dmm.write(f"CALC:FUNC {function}")

    def math_set_dbm_ref(self, resistance):
        self.dmm.write(f"CALC:DBM:REF {resistance}")

    def math_set_null_offset(self, value=None):
        """If value is None, uses current reading as null value."""
        if value is not None:
            self.dmm.write(f"CALC:NULL:OFFS {value}")
        else:
            # This requires the meter to have a valid reading first
            print("Warning: Setting NULL offset requires a valid reading first.")

    def math_get_average_data(self):
        """Returns (min, max, average, count) from the AVERage math function."""
        min_val = float(self.dmm.query("CALC:AVER:MIN?"))
        max_val = float(self.dmm.query("CALC:AVER:MAX?"))
        avg_val = float(self.dmm.query("CALC:AVER:AVER?"))
        cnt_val = float(self.dmm.query("CALC:AVER:COUN?"))
        return {"min": min_val, "max": max_val, "avg": avg_val, "count": cnt_val}

    # ==========================================
    # System & Utility
    # ==========================================

    def beep(self):
        self.dmm.write("SYST:BEEP")

    def system_get_error(self):
        """Reads and clears one error from the error queue."""
        return self.dmm.query("SYST:ERR?")

    def display_text(self, text):
        """Write text to the VFD display."""
        self.dmm.write(f'DISP:TEXT "{text}"')

    def display_clear(self):
        self.dmm.write("DISP:TEXT:CLE")

    # ==========================================
    # User Recipes (Preserved & Updated)
    # ==========================================
    
    def configure_high_accuracy_dc_voltage(self, range_val=10):
        """Recipe: Setup for max accuracy DC Voltage."""
        self.configure_voltage_dc(range_val)
        self.set_nplc(100, "VOLT:DC")            # Maximum integration time
        self.set_autozero("ON")                  # Enable autozero
        self.set_input_impedance_auto(True)      # High impedance (>10G)
        
        print(f"Configured for high-accuracy DC voltage, {range_val}V range")
    
    def fast_dc_voltage_measurement(self, samples=100):
        """Recipe: Burst measurement for max speed."""
        self.configure_voltage_dc()
        self.set_nplc(0.02, "VOLT:DC")           # Minimum integration time
        self.set_autozero("OFF")                 # Disable autozero for speed
        self.set_sample_count(samples)
        self.set_trigger_delay(0)
        
        # Trigger and read all samples
        print(f"Acquiring {samples} samples...")
        start_time = time.time()
        
        # READ? initiates and transfers data
        response = self.read()
        
        measurement_time = time.time() - start_time
        
        # Parse results
        try:
            values = [float(x) for x in response.split(',')]
            rate = len(values) / measurement_time
            print(f"Fast measurement: {rate:.0f} samples/second")
            return values
        except ValueError:
            print("Error parsing response")
            return []
    
    def measure_with_statistics(self, measurement_type="VOLT:DC", samples=20):
        """Recipe: Take multiple samples and calculate stats in Python."""
        # Map user string to SCPI function string if needed, or assume valid
        
        self.dmm.write(f"CONF:{measurement_type}")
        
        if "VOLT:DC" in measurement_type:
            self.set_nplc(10, "VOLT:DC")  # Good balance of speed/accuracy
        
        measurements = []
        print(f"Taking {samples} {measurement_type} measurements...")
        
        for i in range(samples):
            # Use READ? for individual triggered measurements
            value = float(self.read())
            measurements.append(value)
            print(f"  #{i+1}: {value:.8f}")
            time.sleep(0.1)
        
        # Calculate statistics
        if not measurements:
            return {}
            
        stats = {
            'mean': statistics.mean(measurements),
            'stdev': statistics.stdev(measurements) if len(measurements) > 1 else 0,
            'min': min(measurements),
            'max': max(measurements),
            'range': max(measurements) - min(measurements),
            'samples': measurements
        }
        
        return stats
    
    def close(self):
        try:
            self.dmm.close()
            self.rm.close()
        except:
            pass