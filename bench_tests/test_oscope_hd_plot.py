import matplotlib.pyplot as plt
from bench.visa_manager import VisaManager
from bench.instrument_setup import instrument_factory

# YOUR SCOPE ID
ID_SCOPE = "USB0::0x0699::0x0378::C011758::INSTR"

# Tektronix Standard Colors (Optimized for White Background)
CH_COLORS = {
    1: '#E6A800', # Ch1: Darker Yellow/Gold (Visible on white)
    2: '#005AB5', # Ch2: Cyan/Blue
    3: '#DC005E', # Ch3: Magenta/Purple
    4: '#008000'  # Ch4: Green
}

def main():
    vm = VisaManager()
    print("Connecting to Scope...")
    
    try:
        scope = instrument_factory(vm.open(ID_SCOPE))
        print("✅ Connected.")

        # Setup Plot
        plt.figure(figsize=(10, 6), dpi=150)
        plt.title("Multi-Channel Waveform Capture", fontsize=16)
        plt.xlabel("Time (s)", fontsize=12)
        plt.ylabel("Voltage (V)", fontsize=12)
        plt.grid(True, which='both', linestyle='--', alpha=0.7)

        channels_found = 0

        # Loop through all 4 channels
        for ch in [1, 2, 3, 4]:
            # 1. Check if Channel is ON
            if scope.is_channel_on(ch):
                print(f"📥 Downloading Channel {ch}...", end="", flush=True)
                
                # 2. Download Data (Using the Binary method)
                times, volts = scope.read_waveform(channel=ch)
                
                if len(times) > 0:
                    print(f" Done ({len(times)} points).")
                    
                    # 3. Plot it
                    plt.plot(times, volts, 
                             color=CH_COLORS[ch], 
                             linewidth=1.5, 
                             label=f"Channel {ch}")
                    channels_found += 1
                else:
                    print(" Error (No data).")
            else:
                # Skip off channels
                pass

        if channels_found > 0:
            plt.legend()
            filename = "4Channel_Capture.png"
            plt.savefig(filename, dpi=300)
            print(f"\n✅ Saved Image: {filename}")
            plt.show()
        else:
            print("\n⚠️ No channels were active! Turn on a channel and try again.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        try:
            scope.close()
        except:
            pass

if __name__ == "__main__":
    main()