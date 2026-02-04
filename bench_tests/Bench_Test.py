import time
from bench.visa_manager import VisaManager
from bench.instrument_setup import instrument_factory

# --- YOUR HARDWARE IDs ---
ID_AWG   = "USB0::0xF4EC::0xEE38::574C20107::INSTR"
ID_SCOPE = "USB0::0x0699::0x0378::C011758::INSTR"
ID_PSU   = "GPIB0::3::INSTR"
ID_DMM   = "GPIB0::20::INSTR"

def main():
    vm = VisaManager()
    print("--- Connecting to Instruments ---")

    # 1. Connect AWG
    try:
        print(f"Connecting to AWG ({ID_AWG})...")
        awg_inst = vm.open(ID_AWG)
        awg = instrument_factory(awg_inst)
        print(f"✅ Success: {awg.idn()}")
    except Exception as e:
        print(f"❌ AWG Failed: {e}")
        return

    # 2. Connect Scope (FIX: Increase timeout to 20 seconds)
    try:
        print(f"Connecting to Scope ({ID_SCOPE})...")
        # FIX: Added timeout=20000 (20 seconds) to prevent timeout during Autoset
        scope_inst = vm.open(ID_SCOPE, timeout=20000) #
        scope = instrument_factory(scope_inst)
        print(f"✅ Success: {scope.idn()}")
    except Exception as e:
        print(f"❌ Scope Failed: {e}")
        return

    # 3. Run Test: Generate Sine Wave
    print("\n--- Running Test ---")
    try:
        # Setup Generator: 1kHz, 2Vpp Sine Wave
        print("Setting AWG Ch1: Sine, 1kHz, 2Vpp...")
        awg.set_waveform("SINE", channel=1)     #
        awg.set_frequency(1000, channel=1)      #
        awg.set_amplitude_vpp(2.0, channel=1)   #
        awg.output_on(channel=1)                #

        # FIX: Increased wait time to 6 seconds to let Scope settle
        print("Waiting for signal to stabilize...")
        time.sleep(2) 

        # Setup Scope to measure
        print("Autosetting Scope (This takes a few seconds)...")
        scope.set_channel_on(1)                 #
        scope.autoset()                         #
        
        # FIX: Wait 8 seconds for the mechanical relays to finish clicking
        time.sleep(8) 
        
        # Measure
        print("Reading Measurement...")
        scope.configure_measurement(ch=1, meas_type="PK2PK") #
        vpp = scope.get_measurement_value()                  #
        
        print(f"\nMeasured Vpp: {vpp:.4f} V")
        
        if 1.8 < vpp < 2.2:
            print("✅ TEST PASSED: Signal detected!")
        else:
            print("⚠️ TEST WARNING: Signal out of expected range (Check BNC cable).")

    except Exception as e:
        print(f"Test Error: {e}")

    finally:
        # Cleanup
        print("\nTurning off Output...")
        try:
            awg.output_off(channel=1)
            awg_inst.close()
            scope_inst.close()
        except:
            pass

if __name__ == "__main__":
    main()