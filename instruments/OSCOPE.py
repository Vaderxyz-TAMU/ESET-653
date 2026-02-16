import pyvisa
import time
import numpy as np

class OSCOPE:
    def __init__(self, resource_string):
        self.rm = pyvisa.ResourceManager()
        try:
            self.rm.list_resources()
            self.scope = self.rm.open_resource(resource_string)
            self.scope.timeout = 10000 # 10 seconds

            # Standard SCPI Initialization
            self.scope.write('*CLS')  # Clear Status
            self.scope.write('*RST')  # Reset to Factory Default (Optional, usually safer)
            time.sleep(2)             # Wait for reset
            
            self.scope.write('HEADER OFF') # Disable headers for easier parsing
            print(f"Connected to: {self.scope.query('*IDN?').strip()}")

        except pyvisa.VisaIOError as e:
            print(f"Could not connect to {resource_string}")
            raise e
        
    # ==========================================
    # SYSTEM & UTILITY COMMANDS
    # ==========================================
    def run(self):
        """Starts acquisition."""
        self.scope.write('ACQuire:STATE RUN')

    def stop(self):
        """Stops acquisition."""
        self.scope.write('ACQuire:STATE STOP')

    def single(self):
        """Sets to Single Sequence mode and runs once."""
        self.scope.write('ACQuire:STOPAfter SEQuence')
        self.scope.write('ACQuire:STATE RUN')

    def autoset(self):
        """Performs an Autoset (like pushing the button)."""
        self.scope.write('AUTOSet EXECute')
        time.sleep(2) # Autoset takes time

    def write_command(self, command):
        """Send raw SCPI command."""
        self.scope.write(command)

    def query_command(self, command):
        """Send raw SCPI query."""
        return self.scope.query(command).strip()

    # ==========================================
    # ACQUISITION COMMAND GROUP
    # ==========================================
    def configure_acquisition(self, mode='SAMPLE', num_avg=16):
        """
        Configures how data is captured.
        mode: 'SAMPLE', 'PEAKDETECT', 'AVERAGE', 'HIRES'
        """
        self.scope.write(f'ACQuire:MODe {mode}')
        if mode == 'AVERAGE':
            self.scope.write(f'ACQuire:NUMAVg {num_avg}')

    def configure_timebase(self, scale=None, position=None):
        """
        scale: Horizontal scale (seconds/div)
        position: Horizontal position (seconds from trigger)
        """
        if scale:
            self.scope.write(f'HORizontal:SCALe {scale}')
        if position:
            self.scope.write(f'HORizontal:POSition {position}')

   # =========================================================================
    # VERTICAL COMMAND GROUP (ANALOG)
    # =========================================================================
    def configure_channel(self, channel, scale=None, position=None, coupling=None, probe_atten=None, bandwidth=None):
        """
        Configures Vertical settings for Analog Channels (CH1-CH4).

        :param channel: Channel number (1, 2, 3, or 4).
        :param scale: Vertical channel scale in units-per-division (e.g., 1.0 for 1V/div). 
                      The value is truncated to three significant digits.
        :param position: Vertical position in divisions from the center graticule. 
                         Range is -4.0 to 4.0 divisions. 
        :param coupling: Sets the input connection. Valid: 'DC', 'AC', or 'GND'.
        :param probe_atten: Manual probe attenuation factor (e.g., 10 for a 10x probe).
                            The command sets gain as 1/attenuation.
        :param bandwidth: Sets the upper bandwidth limit to reduce noise. 
                          Common values: 'FULL' or '20MHz'.
        """
        ch_str = f"CH{channel}"
        
        # SELect:CH<x> ON turns the channel waveform display on and selects the channel.
        self.scope.write(f'SELect:{ch_str} ON')

        # CH<x>:COUPling sets the coupling for the specified channel.
        if coupling:
            self.scope.write(f'{ch_str}:COUPling {coupling}')
            
        # CH<x>:SCAle sets the vertical sensitivity in units per division.
        if scale:
            self.scope.write(f'{ch_str}:SCALe {scale}')
            
        # CH<x>:POSition sets the vertical display position relative to center (in divisions). 
        if position:
            self.scope.write(f'{ch_str}:POSition {position}')
            
        # CH<x>:PRObe:GAIN sets the gain for the attached probe (inverse of attenuation).
        if probe_atten:
             # Manually set probe attenuation (1, 10, etc.) if not using a TekVPI smart probe.
            self.scope.write(f'{ch_str}:PRObe:GAIN {1.0/probe_atten}')
            
        # CH<x>:BANdwidth limits the channel bandwidth to the specified frequency.
        if bandwidth:
            self.scope.write(f'{ch_str}:BANdwidth {bandwidth}')

    # ==========================================
    # DIGITAL COMMAND GROUP (MSO ONLY)
    # ==========================================
    def configure_digital(self, d_channel, state='ON', threshold_volts=1.4, height='S'):
        """
        Configures Digital Channels (D0-D15) for MSO models.
        d_channel: 0 to 15
        threshold_volts: Logic threshold (e.g., 1.4 for TTL)
        height: 'S' (Small), 'M' (Medium), 'L' (Large) display height
        """
        # Select/Turn on the digital channel
        self.scope.write(f'SELect:D{d_channel} {state}')
        
        if state == 'ON':
            # Set Threshold
            self.scope.write(f'DIGital:D{d_channel}:THReshold {threshold_volts}')
            # Set Display Height
            self.scope.write(f'DIGital:D{d_channel}:POSition {height}')

    # ==========================================
    # TRIGGER COMMAND GROUP
    # ==========================================
    def configure_trigger_edge(self, source='CH1', level=0.0, slope='RISE', mode='AUTO', coupling='DC'):
        """
        Configures a standard Edge Trigger.
        """
        ch_str = f"CH{source}"

        self.scope.write('TRIGger:A:TYPe EDGE')
        self.scope.write(f'TRIGger:A:EDGE:SOUrce {ch_str}')
        self.scope.write(f'TRIGger:A:EDGE:COUPling {coupling}')
        self.scope.write(f'TRIGger:A:EDGE:SLOPE {slope}')
        self.scope.write(f'TRIGger:A:LEVel {level}')
        self.scope.write(f'TRIGger:A:MODe {mode}')
        
        print(f"Trigger set: {source} @ {level}V ({slope}) - {mode}")

    def force_trigger(self):
        """Forces a trigger event (useful in Normal mode)."""
        self.scope.write('TRIGger:FORce')

    # ==========================================
    # MEASUREMENT COMMAND GROUP
    # ==========================================
    def add_measurement(self, slot, meas_type, source1):
        """
        Adds a measurement to the scope screen.
        slot: 1, 2, 3, or 4 (The MSO2000 has 4 measurement slots)
        meas_type: 'FREQUENCY', 'PERIOD', 'MEAN', 'PK2PK', 'CRMS', 'MAX', 'MIN', 'RISE', 'FALL'
        """
        self.scope.write(f'MEASUrement:MEAS{slot}:TYPe {meas_type}')
        self.scope.write(f'MEASUrement:MEAS{slot}:SOUrce {source1}')
        self.scope.write(f'MEASUrement:MEAS{slot}:STATE ON')

    def get_measurement_value(self, slot):
        """Reads the value of an on-screen measurement slot."""
        try:
            val = float(self.scope.query(f'MEASUrement:MEAS{slot}:VALue?'))
            if val > 9.0e30: # Tektronix uses high values for Infinity/NaN
                return None
            return val
        except:
            return None

    def get_immediate_measurement(self, source, meas_type):
        """
        Takes a quick measurement without adding it to the screen slots.
        """
        self.scope.write(f'MEASUrement:IMMed:SOUrce1 {source}')
        self.scope.write(f'MEASUrement:IMMed:TYPe {meas_type}')
        time.sleep(0.1) # Wait for calc
        try:
            val = float(self.scope.query('MEASUrement:IMMed:VALue?'))
            return val if val < 9.0e30 else None
        except:
            return None

    # ==========================================
    # WAVEFORM TRANSFER GROUP
    # ==========================================
    def acquire_waveform(self, source='CH1'):
        """
        Downloads waveform data from the scope to numpy arrays.
        Handles Scaling (Preamble) automatically.
        """
        self.scope.write(f'DATa:SOUrce {source}')
        self.scope.write('DATa:ENCdg RIBINARY') # Signed Integer Binary
        self.scope.write('DATa:WIDth 1')        # 1 Byte per point (Speed)
        
        # Set start and stop points to full record
        record_len = int(self.scope.query('HORizontal:RECOrdlength?'))
        self.scope.write('DATa:STARt 1')
        self.scope.write(f'DATa:STOP {record_len}')

        # Get Preamble (Scaling factors)
        ymult = float(self.scope.query('WFMOutpre:YMUlt?'))
        yoff = float(self.scope.query('WFMOutpre:YOFf?'))
        yzero = float(self.scope.query('WFMOutpre:YZEro?'))
        xincr = float(self.scope.query('WFMOutpre:XINcr?'))
        xzero = float(self.scope.query('WFMOutpre:XZEro?'))

        # Fetch Binary Data
        # 'b' = signed char (1 byte)
        raw_data = self.scope.query_binary_values(
            'CURVe?', datatype='b', is_big_endian=True, container=np.array
        )

        # Convert Raw ADC values to Volts
        # Formula: Volts = (Raw - YOff) * YMult + YZero
        volts = (raw_data - yoff) * ymult + yzero
        
        # Create Time Axis
        time_axis = xzero + (np.arange(len(volts)) * xincr)

        return time_axis, volts

    # ==========================================
    # DISPLAY & HARDCOPY GROUP
    # ==========================================
    def save_screenshot(self, filename="scope_screen.png"):
        """
        Saves the current screen image to the PC.
        Refined to use read_raw() since the scope sends raw PNG bytes, 
        not an IEEE 488.2 block.
        """
        try:
            # 1. Configure Hardcopy to send PNG
            self.scope.write('HARDCopy:FORMat PNG')
            self.scope.write('HARDCopy:LAYout LANdscape')
            
            # Note: 'HARDCopy:PORT' settings can vary by firmware/connection. 
            # If the command below causes a timeout, try commenting it out.
            self.scope.write('HARDCopy:PORT USB') 

            # 2. Request the data
            self.scope.write('HARDCopy STARt')
            
            # 3. Read the raw byte stream directly
            # We do not use query_binary_values because there is no header block
            raw_data = self.scope.read_raw()
            
            # 4. Save to file
            with open(filename, 'wb') as f:
                f.write(raw_data)
            
            print(f"Screenshot saved to {filename}")

        except pyvisa.VisaIOError as e:
            print(f"Screenshot failed: {e}")

    def measure_delay(self, start_src='CH1', stop_src='CH2', start_edge='RISE', stop_edge='RISE'):
        """
        Measures the time delay between two events.
        Equivalent to Keysight's: MEAS:DEF DEL, +1, +1 (if both edges are RISE)
        
        Parameters:
        start_src: 'CH1', 'CH2', 'MATH', etc.
        stop_src:  'CH1', 'CH2', etc.
        start_edge: 'RISE' (same as +1) or 'FALL' (same as -1)
        stop_edge:  'RISE' (same as +1) or 'FALL' (same as -1)
        """

        ch_str1 = f"CH{start_src}"
        ch_str2 = f"CH{stop_src}"
        
        # 1. Set Type to Delay
        self.scope.write('MEASUrement:IMMed:TYPe DELay')
        
        # 2. Configure Start Point (Source 1)
        self.scope.write(f'MEASUrement:IMMed:SOUrce1 {ch_str1}')
        self.scope.write(f'MEASUrement:IMMed:DELay:EDGE1 {start_edge}')
        
        # 3. Configure Stop Point (Source 2)
        self.scope.write(f'MEASUrement:IMMed:SOUrce2 {ch_str2}')
        self.scope.write(f'MEASUrement:IMMed:DELay:EDGE2 {stop_edge}')
        
        # 4. Optional: Set Direction (FORWARD forces the measurement to the NEXT edge)
        self.scope.write('MEASUrement:IMMed:DELay:DIRection FORWard')

        # 5. Wait for measurement to stabilize
        time.sleep(0.1)
        
        # 6. Query Value
        try:
            val = float(self.scope.query('MEASUrement:IMMed:VALue?'))
            if val > 9.0e30: return None # No edge found
            return val
        except:
            return None

    # ==========================================
    # CALCULATED MEASUREMENTS GROUP
    # ==========================================
    def measure_switching_parameters(self, ch_input, ch_output):
        """
        Calculates tON, tRise, tDelay (manual 50% to 10%), tOFF, and tFall.
        
        Args:
            ch_input (int): The channel number of the input signal (e.g., 1).
            ch_output (int): The channel number of the output signal (e.g., 2).
            
        Returns:
            dict: A dictionary containing the measured values in seconds.
        """
        results = {}
        
        # Ensure channels are integers for SCPI commands
        src_in = f"CH{ch_input}"
        src_out = f"CH{ch_output}"

        try:
            # --- 1. tON (Turn-On Delay: 50% Rise to 50% Rise) ---
            # Using the standard delay measurement
            self.scope.write(f'MEASUrement:IMMed:TYPe DELay')
            self.scope.write(f'MEASUrement:IMMed:SOUrce1 {src_in}')
            self.scope.write(f'MEASUrement:IMMed:SOUrce2 {src_out}')
            self.scope.write('MEASUrement:IMMed:DELay:EDGE1 RISE')
            self.scope.write('MEASUrement:IMMed:DELay:EDGE2 RISE')
            results['tON'] = float(self.scope.query('MEASUrement:IMMed:VALue?'))

            # --- 2. tRise (Rise Time: 10% to 90%) ---
            self.scope.write('MEASUrement:IMMed:TYPe RISe')
            self.scope.write(f'MEASUrement:IMMed:SOUrce1 {src_out}')
            results['tRise'] = float(self.scope.query('MEASUrement:IMMed:VALue?'))

            # --- 3. tDelay (Manual Calculation: Input 50% to Output 10%) ---
            # A. Acquire Data
            self.scope.write(f'DATA:SOUrce {src_in}')
            raw_in = self.scope.query('CURVe?')
            vals_in = np.array([float(val) for val in raw_in.split(',')])

            self.scope.write(f'DATA:SOUrce {src_out}')
            raw_out = self.scope.query('CURVe?')
            vals_out = np.array([float(val) for val in raw_out.split(',')])

            # B. Get Timing
            x_incr = float(self.scope.query('WFMPRe:XINcr?'))

            # C. Find Thresholds (50% for Input, 10% for Output)
            min_in, max_in = np.min(vals_in), np.max(vals_in)
            thresh_50_in = min_in + (max_in - min_in) * 0.50
            
            min_out, max_out = np.min(vals_out), np.max(vals_out)
            thresh_10_out = min_out + (max_out - min_out) * 0.10

            # D. Find Indices
            # Note: Using try/except to handle cases where signal doesn't cross threshold
            try:
                idx_in = np.where(vals_in >= thresh_50_in)[0][0]
                idx_out = np.where(vals_out >= thresh_10_out)[0][0]
                results['tDelay'] = (idx_out - idx_in) * x_incr
            except IndexError:
                results['tDelay'] = 0.0 # Or float('nan') if preferred

            # --- 4. tOFF (Turn-Off Delay: 50% Fall to 50% Fall) ---
            self.scope.write(f'MEASUrement:IMMed:TYPe DELay')
            self.scope.write(f'MEASUrement:IMMed:SOUrce1 {src_in}')
            self.scope.write(f'MEASUrement:IMMed:SOUrce2 {src_out}')
            self.scope.write('MEASUrement:IMMed:DELay:EDGE1 FALL')
            self.scope.write('MEASUrement:IMMed:DELay:EDGE2 FALL')
            results['tOFF'] = float(self.scope.query('MEASUrement:IMMed:VALue?'))

            # --- 5. tFall (Fall Time: 90% to 10%) ---
            self.scope.write('MEASUrement:IMMed:TYPe FALl')
            self.scope.write(f'MEASUrement:IMMed:SOUrce1 {src_out}')
            results['tFall'] = float(self.scope.query('MEASUrement:IMMed:VALue?'))

            return results

        except Exception as e:
            print(f"Error during measurement: {e}")
            return None

    def close(self):
        self.scope.close()
        self.rm.close()