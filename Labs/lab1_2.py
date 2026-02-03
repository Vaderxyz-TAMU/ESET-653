import pyvisa
import time
import csv
from datetime import datetime

class TestSequenceController:
    def __init__(self):
        self.instruments = {}
        self.rm = pyvisa.ResourceManager()
    
    def add_instrument(self, name, resource_string, **config):
        try:
            inst = self.rm.open_resource(resource_string)
            if 'timeout' in config:
                inst.timeout = config['timeout']
            if 'termination' in config:
                inst.read_termination = config['termination']
                inst.write_termination = config['termination']
            self.instruments[name] = inst
            print(f"Added {name}: {inst.query('*IDN?').strip()}")
        except Exception as e:
            print(f"Error connecting to {name}: {e}")

    def run_ron_test_sequence(self, filename="Ron Results.csv", num_samples=10):
        """
        Runs the test sequence with averaging.
        num_samples: Number of readings to average per step (default 10)
        """
        psu = self.instruments.get('power_supply')
        sig_gen = self.instruments.get('signal_generator')
        dmm = self.instruments.get('dmm')

        if not all([psu, sig_gen, dmm]):
            print("Error: Missing required instruments.")
            return

        # Define steps with prompts
        # psu_volts: Voltage for Power Supply
        # sg_ch1: Voltage (Offset) for Sig Gen Channel 1
        # sg_ch2: Voltage (Offset) for Sig Gen Channel 2
        test_steps = [
            {'psu_volts': 5.0, 'sg_ch1': 5.0, 'sg_ch2': 0.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP3 & TP7 (Config A)"},
            {'psu_volts': 2.5, 'sg_ch1': 5.0, 'sg_ch2': 0.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP3 & TP7 (Config A)"},
            
            {'psu_volts': 5.0, 'sg_ch1': 0.0, 'sg_ch2': 5.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP3 & TP7 (Config A)"},
            {'psu_volts': 2.5, 'sg_ch1': 0.0, 'sg_ch2': 5.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP3 & TP7 (Config A)"},

            {'psu_volts': 5.0, 'sg_ch1': 5.0, 'sg_ch2': 5.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP3 & TP7 (Config A)"},
            {'psu_volts': 2.5, 'sg_ch1': 5.0, 'sg_ch2': 5.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP3 & TP7 (Config A)"},

            
            {'psu_volts': 5.0, 'sg_ch1': 5.0, 'sg_ch2': 0.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP4 & TP8 (Config B)"},
            {'psu_volts': 2.5, 'sg_ch1': 5.0, 'sg_ch2': 0.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP4 & TP8 (Config B)"},
            
            {'psu_volts': 5.0, 'sg_ch1': 0.0, 'sg_ch2': 5.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP4 & TP8 (Config B)"},
            {'psu_volts': 2.5, 'sg_ch1': 0.0, 'sg_ch2': 5.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP4 & TP8 (Config B)"},

            {'psu_volts': 5.0, 'sg_ch1': 5.0, 'sg_ch2': 5.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP4 & TP8 (Config B)"},
            {'psu_volts': 2.5, 'sg_ch1': 5.0, 'sg_ch2': 5.0, 'curr_lim': 1.0, 'prompt': "Connect probes to TP4 & TP8 (Config B)"},

        ]

        # Basic Instrument Setup
        # We set the wave type to DC once, but we update the OFFSET (Voltage) in the loop
        sig_gen.write("C1:BSWV WVTP,DC")
        sig_gen.write("C2:BSWV WVTP,DC")
        
        dmm.write("CONF:VOLT:DC")

        print(f"Starting test with {num_samples}-sample averaging. Saving to {filename}...")
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "PSU Set (V)", "SG Ch1 (V)", "SG Ch2 (V)", "Avg Voltage (V)", "Avg Current (A)", "Ron (Ohms)"])

            for i, step in enumerate(test_steps):
                # --- PAUSE FOR PROBE CHANGE ---
                print(f"\n--- Step {i+1} Preparation ---")
                
                # Safety: Everything OFF
                psu.write("OUTP OFF") 
                sig_gen.write("C1:OUTP OFF")
                sig_gen.write("C2:OUTP OFF")  

                input(f"ACTION: {step['prompt']}\nPress [ENTER] to measure...")
                
                # --- APPLY SETTINGS ---
                # 1. Update Signal Generator Voltages (Offsets)
                sig_gen.write(f"C1:BSWV OFST,{step['sg_ch1']}")
                sig_gen.write(f"C2:BSWV OFST,{step['sg_ch2']}")
                
                # 2. Turn Gate ON
                sig_gen.write("C1:OUTP ON")
                sig_gen.write("C2:OUTP ON")
                
                # 3. Set PSU and Turn ON
                psu.write(f"VOLT {step['psu_volts']}")
                psu.write(f"CURR {step['curr_lim']}") 
                psu.write("OUTP ON")
                
                time.sleep(1.0)  # Wait for voltage to settle

                # --- AVERAGING LOOP ---
                print(f"Taking {num_samples} readings (PSU: {step['psu_volts']}V, SG1: {step['sg_ch1']}V, SG2: {step['sg_ch2']}V)...")
                total_volts = 0.0
                total_curr = 0.0

                for s in range(num_samples):
                    # Measure Voltage
                    dmm.write("READ?")
                    v_reading = float(dmm.read())
                    total_volts += v_reading

                    # Measure Current
                    # Note: Ensure this P6V query matches your hardware channel
                    i_reading = float(psu.query("MEAS:CURR:DC? P6V"))
                    total_curr += i_reading
                    
                    time.sleep(0.1)

                # Calculate Averages
                avg_volts = total_volts / num_samples
                avg_curr = total_curr / num_samples

                # Calculate Resistance
                if avg_curr > 1e-9:
                    r_on = avg_volts / avg_curr
                else:
                    r_on = float('inf')

                # Save Average Data
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [timestamp, step['psu_volts'], step['sg_ch1'], step['sg_ch2'], avg_volts, avg_curr, r_on]
                writer.writerow(row)
                
                print(f"Result: {avg_volts:.4f}V / {avg_curr:.4f}A = {r_on:.4f} Ohms")

        # Final Cleanup
        print("\nTest Complete. Turning off outputs.")
        psu.write("OUTP OFF")
        sig_gen.write("C1:OUTP OFF")
        sig_gen.write("C2:OUTP OFF")
        sig_gen.write("OUTP OFF") # Global off if supported

    def close_all(self):
        for name, inst in self.instruments.items():
            try:
                inst.close()
            except:
                pass
        self.rm.close()

# --- Usage Example ---
if __name__ == "__main__":
    controller = TestSequenceController()
    try:
        # Update your addresses here
        controller.add_instrument('power_supply', 'GPIB0::3::INSTR')
        controller.add_instrument('signal_generator', 'USB0::0xF4EC::0xEE38::574C20107::INSTR')
        controller.add_instrument('dmm', 'GPIB0::20::INSTR')
        
        # Run with 10 samples per step
        controller.run_ron_test_sequence(num_samples=10)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        controller.close_all()