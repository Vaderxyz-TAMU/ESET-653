import time
from bench.visa_manager import VisaManager
from bench.instrument_setup import instrument_factory

# YOUR SPECIFIC PSU ID
ID_PSU = "GPIB0::3::INSTR"

def test_channel(psu, channel, voltage, current_limit):
    """Helper to test a specific rail."""
    print(f"\n--- Testing Channel {channel} ---")
    
    try:
        # 1. Set Values using the new robust method
        print(f"Setting {voltage}V / {current_limit}A on {channel}...")
        psu.set_voltage(voltage, channel=channel)   #
        psu.set_current(current_limit, channel=channel) #
        
        # 2. Verify Internal Measurement
        time.sleep(1) # Wait for voltage to rise
        meas_v = psu.measure_voltage(channel=channel) #
        meas_i = psu.measure_current(channel=channel) #
        
        print(f"Readback: {meas_v:.4f} V (Expected: {voltage} V)")
        
        # 3. Validation Logic
        error = abs(meas_v - voltage)
        if error < 0.1: # Allow 100mV tolerance
            print(f"✅ {channel} Passed")
        else:
            print(f"❌ {channel} Failed: Variance {error:.4f}V")
            
    except Exception as e:
        print(f"❌ {channel} Error: {e}")

def main():
    vm = VisaManager()
    print("Connecting to Power Supply...")
    
    try:
        # Connect
        psu_inst = vm.open(ID_PSU)
        psu = instrument_factory(psu_inst)
        print(f"Connected: {psu.idn()}")
        
        # Reset and Safety Setup
        psu.reset() #
        psu.output_off()
        
        # Example: Set Global Safety Limits
        # This prevents accidental 20V spikes on your 5V logic board
        psu.set_safety_limits(max_voltage=26.0, max_current=1.0) #
        
        psu.output_on() #
        time.sleep(1)

        # --- TEST 1: The 6V Rail (Logic) ---
        test_channel(psu, "P6V", 3.3, 0.5)

        # --- TEST 2: The +25V Rail (Op-Amps) ---
        test_channel(psu, "P25V", 12.0, 0.1)

        # --- TEST 3: The -25V Rail (Negative Rail) ---
        # Note: We send -12.0, but the method handles it
        test_channel(psu, "N25V", -12.0, 0.1)

        # --- TEST 4: Safety Trip Check ---
        print("\n--- Testing Software Safety Limits ---")
        try:
            print("Attempting to set 35V (Limit is 26V)...")
            psu.set_voltage(35.0, channel="P25V")
            print("❌ FAILED: Driver allowed dangerous voltage!")
        except ValueError as e:
            print(f"✅ PASSED: Driver blocked command: {e}")

    except Exception as e:
        print(f"Main Error: {e}")

    finally:
        print("\nTurning Outputs OFF...")
        try:
            psu.set_voltage(0, "P6V")
            psu.set_voltage(0, "P25V")
            psu.set_voltage(0, "N25V")
            psu.output_off()
            psu.close()
        except:
            pass

if __name__ == "__main__":
    main()