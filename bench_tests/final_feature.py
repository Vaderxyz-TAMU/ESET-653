import time
import os
import matplotlib.pyplot as plt
from bench.visa_manager import VisaManager
from bench.instrument_setup import instrument_factory

# --- HARDWARE IDs ---
ID_AWG   = "USB0::0xF4EC::0xEE38::574C20107::INSTR"
ID_SCOPE = "USB0::0x0699::0x0378::C011758::INSTR"
ID_PSU   = "GPIB0::3::INSTR"
ID_DMM   = "GPIB0::20::INSTR"

def test_psu(vm):
    print("\n--- 1. Testing Power Supply (E3631A) ---")
    try:
        psu = instrument_factory(vm.open(ID_PSU))
        print(f"   Connected: {psu.idn()}")
        
        # Test Internal Metering (Works even without load)
        print("   Testing Rails (Internal Readback):")
        
        # P6V Rail
        psu.set_voltage(5.0, channel="P6V")
        psu.set_current(0.1, channel="P6V")
        psu.output_on()
        time.sleep(1) # Wait for voltage to rise
        meas = psu.measure_voltage("P6V")
        print(f"   -> Set 5.0V on P6V, Read: {meas:.4f}V", end="")
        if 4.9 < meas < 5.1: print(" [PASS]")
        else: print(" [FAIL] (Internal Reg Failure)")

        # P25V Rail
        psu.set_voltage(24.0, channel="P25V")
        time.sleep(1)
        meas = psu.measure_voltage("P25V")
        print(f"   -> Set 24.0V on P25V, Read: {meas:.4f}V", end="")
        if 23.9 < meas < 24.1: print(" [PASS]")
        else: print(" [FAIL]")

        psu.output_off()
        psu.close()
        print("   ✅ PSU Tests Complete.")
    except Exception as e:
        print(f"   ❌ PSU Failed: {e}")

def test_awg(vm):
    print("\n--- 2. Testing Generator (BK 4063B) ---")
    try:
        awg = instrument_factory(vm.open(ID_AWG))
        print(f"   Connected: {awg.idn()}")
        
        # Test Syntax Acceptance (Did the machine understand us?)
        print("   Sending complex configuration...")
        awg.configure_pwm(freq=1000, vpp=3.0, duty_cycle=25, channel=1)
        awg.output_on(channel=1)
        
        # Check Error Queue
        # If your AWG.py has typos (like TYPE instead of WVTP), this will catch it.
        try:
            err = awg.query("SYST:ERR?")
            if "0" in err or "No error" in err:
                 print("   -> Syntax Check: [PASS] (Device accepted all commands)")
            else:
                 print(f"   -> Syntax Check: [FAIL] Device reported: {err.strip()}")
        except:
            print("   -> (Device does not support error query, skipping)")

        time.sleep(1)
        awg.output_off()
        awg.close()
        print("   ✅ AWG Tests Complete.")
    except Exception as e:
        print(f"   ❌ AWG Failed: {e}")

def test_dmm(vm):
    print("\n--- 3. Testing Multimeter (34401A) ---")
    try:
        dmm = instrument_factory(vm.open(ID_DMM))
        
        # Visual Check
        dmm.set_text("SYS TEST")
        print("   Display Text Set: 'SYS TEST'")
        
        # Open Circuit Resistance Check
        print("   Measuring Open Circuit Resistance...")
        dmm.configure_resistance()
        res = dmm.read_value()
        
        # 34401A returns +9.90000000E+37 for Infinity
        if res > 1e30:
            print(f"   -> Read: {res:.1E} Ohms (Correct for Open Circuit) [PASS]")
        else:
            print(f"   -> Read: {res} Ohms (Unexpected for Disconnected Probes) [WARN]")

        dmm.clear_text()
        dmm.close()
        print("   ✅ DMM Tests Complete.")
    except Exception as e:
        print(f"   ❌ DMM Failed: {e}")

def test_scope(vm):
    print("\n--- 4. Testing Oscilloscope (MSO2024) ---")
    try:
        scope = instrument_factory(vm.open(ID_SCOPE, timeout=15000))
        
        print("   Initializing Scope (Manual Scale)...")
        scope.set_channel_on(1)
        scope.set_vertical_scale(1, 0.5)
        scope.set_horizontal_scale(100e-6)
        
        # Force Trigger so we can capture "Noise"
        scope.set_trigger_auto()
        time.sleep(3) # Wait for trace
        
        # 1. Test Screenshot
        print("   Testing Screenshot...")
        img_path = os.path.abspath("System_Check_Screen.png")
        scope.save_screenshot(img_path, white_bg=True)
        if os.path.exists(img_path):
             print(f"   -> Image saved: {img_path} [PASS]")
        else:
             print("   -> Image Save Failed [FAIL]")

        # 2. Test Binary Download
        print("   Testing Binary Waveform Download (Channel 1)...")
        times, volts = scope.read_waveform(1)
        
        if len(times) > 1000:
             print(f"   -> Downloaded {len(times)} points via Binary [PASS]")
             
             # Create a quick plot of the noise to verify mapping
             plt.figure(figsize=(6, 3))
             plt.plot(times, volts, color='#E6A800', lw=0.5)
             plt.title(f"Scope Noise Floor Test (Max: {max(volts):.3f}V)")
             plt.tight_layout()
             plt.savefig("System_Check_Trace.png")
             print("   -> Noise trace saved to 'System_Check_Trace.png'")
        else:
             print("   -> Waveform Download Failed [FAIL]")

        scope.close()
        print("   ✅ Scope Tests Complete.")
    except Exception as e:
        print(f"   ❌ Scope Failed: {e}")

def main():
    vm = VisaManager()
    print("=========================================")
    print("      LAB INSTRUMENT SYSTEM CHECK        ")
    print("=========================================")
    
    test_psu(vm)
    test_awg(vm)
    test_dmm(vm)
    test_scope(vm)
    
    print("\n=========================================")
    print("           ALL TESTS FINISHED            ")
    print("=========================================")

if __name__ == "__main__":
    main()