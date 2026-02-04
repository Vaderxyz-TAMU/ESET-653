from bench.base_scpi import SCPIDevice
import time

class TektronixScope(SCPIDevice):
    """
    Robust Driver for Tektronix MSO/DPO 2000/3000/4000 Series.
    """

    def set_horizontal_scale(self, sec_per_div):
        """Sets the timebase (Seconds per Division)."""
        self.write(f"HOR:SCA {sec_per_div}")

    def set_vertical_scale(self, channel, volts_per_div):
        """Sets the vertical scale (Volts per Division)."""
        self.write(f"CH{channel}:SCA {volts_per_div}")

    def set_channel_on(self, channel):
        self.write(f"SEL:CH{channel} ON")

    # --- Triggering ---

    def set_trigger_auto(self):
        """
        Sets trigger to Auto.
        Essential when no signal is connected, otherwise the scope
        waits forever and the screen might freeze.
        """
        self.write("TRIG:A:MOD AUTO")

    # --- Screenshot ---

    def save_screenshot(self, filename="scope_screen.png", white_bg=True):
        """
        Captures the screen and saves it to a file on your PC.
        """
        # 1. Configure Hardcopy parameters
        self.write("HARDC:FORM PNG")             # Explicitly set output format to PNG
        self.write("HARDC:LAY LAND")             # Landscape orientation
        
        # Ink Saver (White background)
        state = "ON" if white_bg else "OFF"
        self.write(f"HARDC:INKS {state}")

        # 2. Prepare for Binary Read
        # CRITICAL: We must disable the read termination character (newline)
        # otherwise Python stops reading when it sees a random '0x0A' byte in the image.
        old_term = self.inst.read_termination
        self.inst.read_termination = None
        
        try:
            # 3. Start Data Dump
            self.write("HARDC START")
            
            # 4. Read Raw Data
            # The scope sends the raw image file bytes immediately
            raw_data = self.inst.read_raw()
            
            # 5. Save to File
            with open(filename, "wb") as f:
                f.write(raw_data)
            
            print(f"📸 Screenshot saved: {filename} ({len(raw_data)} bytes)")
            
        except Exception as e:
            print(f"Screenshot failed: {e}")
            
        finally:
            # 6. Restore Termination (Very Important!)
            # If we don't do this, normal commands like *IDN? will break later.
            self.inst.read_termination = old_term

    # --- Waveform Data Transfer (Updated for Binary) ---

    def read_waveform(self, channel):
        """
        Downloads the raw waveform data using robust Binary transfer.
        Returns: (time_array, voltage_array)
        """
        # 1. Select Source & Format
        self.write(f"DATA:SOU CH{channel}")
        self.write("DATA:START 1")
        self.write("DATA:STOP 100000")  # Request up to 100k points
        
        # FIX: Use Signed Integer Binary (RIB) instead of ASCII.
        # This is faster and avoids the 'string to float' error.
        self.write("DATA:ENC RIB")      
        self.write("DATA:WIDTH 1")      # 1 byte per point (sufficient for screen data)
        
        # 2. Get Scaling Factors (To convert raw bits to Volts/Seconds)
        try:
            ymult = float(self.query("WFMPRE:YMULT?")) # Volts per bit
            yoff  = float(self.query("WFMPRE:YOFF?"))  # Vertical offset in bits
            yzero = float(self.query("WFMPRE:YZERO?")) # Vertical offset in Volts
            xincr = float(self.query("WFMPRE:XINCR?")) # Time per point
            xzero = float(self.query("WFMPRE:XZERO?")) # Time start point
        except Exception as e:
            print(f"Error reading waveform preamble: {e}")
            return [], []

        # 3. Fetch Raw Data (Binary)
        # datatype='b' tells PyVISA to read signed 8-bit integers
        try:
            raw_data = self.inst.query_binary_values(
                "CURVE?", 
                datatype='b', 
                is_big_endian=True, 
                container=list
            )
        except Exception as e:
            print(f"Error reading binary curve: {e}")
            return [], []
        
        # 4. Convert to Real World Units
        voltage_data = []
        time_data = []
        
        # Optimizing this loop for 10,000+ points
        for i, raw_val in enumerate(raw_data):
            # Formula: Voltage = (RawValue - YOffset_Bits) * Volts_Per_Bit + YOffset_Volts
            volts = (raw_val - yoff) * ymult + yzero
            voltage_data.append(volts)
            
            # Formula: Time = (Index * Time_Per_Point) + Time_Start
            t = (i * xincr) + xzero
            time_data.append(t)
            
        return time_data, voltage_data
    
    def is_channel_on(self, channel):
        """Returns True if the channel is currently displayed."""
        try:
            # The scope returns "1" for ON and "0" for OFF
            state = self.query(f"SEL:CH{channel}?")
            return int(state) == 1
        except:
            return False