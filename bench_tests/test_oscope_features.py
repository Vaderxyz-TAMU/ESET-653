import time
import os
from bench.visa_manager import VisaManager
from bench.instrument_setup import instrument_factory

# --- HARDWARE ID ---
ID_SCOPE = "USB0::0x0699::0x0378::C011758::INSTR"

def main():
    vm = VisaManager()
    print("--- Oscilloscope Connection & Capture Test ---")
    
    try:
        # 1. Connect (High timeout for image transfer)
        # We don't need the AWG for this test
        print(f"Connecting to {ID_SCOPE}...")
        scope = instrument_factory(vm.open(ID_SCOPE, timeout=15000))
        print("✅ Connected.")
        
        # 2. visual Check (Move some settings)
        print("🔧 Adjusting Scale (Watch the screen!)...")
        scope.set_channel_on(1)
        scope.set_vertical_scale(channel=1, volts_per_div=2.0)   # Set to 2V
        scope.set_horizontal_scale(sec_per_div=100e-6)           # Set to 100us
        
        # Force Auto Trigger so we see a trace (even if it's just noise)
        scope.set_trigger_auto()
        
        print("   Settings changed. Waiting 2 seconds...")
        time.sleep(2) 

        # 3. Capture Screenshot
        print("\n📸 Capturing Screenshot...")
        filename = "Test_Capture.png"
        
        # Get absolute path (Fixes the network drive confusion)
        full_path = os.path.abspath(filename)
        
        scope.save_screenshot(full_path, white_bg=True)
        
        if os.path.exists(full_path):
            print(f"✅ Image Saved: {full_path}")
            
            # 4. Open the image safely
            print("   Opening image...")
            try:
                os.startfile(full_path)
            except Exception as e:
                print(f"   (Could not auto-open: {e})")
                print("   Please open the file manually from your folder.")
        else:
            print("❌ Error: File was not saved.")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    finally:
        print("\n🔌 Closing connection...")
        try:
            scope.close()
        except:
            pass

if __name__ == "__main__":
    main()