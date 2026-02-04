import time
from bench.visa_manager import VisaManager
from bench.instrument_setup import instrument_factory

# YOUR SPECIFIC DMM ID
ID_DMM = "GPIB0::20::INSTR"

def main():
    vm = VisaManager()
    print("Connecting to DMM...")
    
    try:
        dmm_inst = vm.open(ID_DMM)
        dmm = instrument_factory(dmm_inst)
        print(f"Connected: {dmm.idn()}")
        
        # 1. Screen Text Test
        print("Writing to Display...")
        dmm.set_text("HELLO LAB")
        time.sleep(2)
        dmm.clear_text()

        # 2. High Impedance Mode (Important for accurate voltage)
        print("Enabling High-Z Mode (>10G Ohm)...")
        dmm.configure_voltage_dc("AUTO")
        dmm.set_high_impedance(True)

        # 3. Burst Read Test
        print("\n--- taking 5 DC Voltage Readings ---")
        for i in range(5):
            val = dmm.read_value()
            print(f"Reading {i+1}: {val:.6f} V")

        # 4. Resistance Test (Manual Config)
        print("\n--- Checking Resistance Mode (2-Wire) ---")
        dmm.configure_resistance(wires=2, range_val="AUTO")
        val = dmm.read_value()
        
        if val > 1e30:
            print(f"Resistance: Open Circuit (Infinity)")
        else:
            print(f"Resistance: {val:.4f} Ohms")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            dmm.clear_text()
            dmm_inst.close()
        except:
            pass

if __name__ == "__main__":
    main()