import time
from bench.visa_manager import VisaManager
from bench.instrument_setup import instrument_factory

# YOUR SPECIFIC AWG ID
ID_AWG = "USB0::0xF4EC::0xEE38::574C20107::INSTR"

def main():
    vm = VisaManager()
    
    print("Connecting to Generator...")
    try:
        gen = instrument_factory(vm.open(ID_AWG))
        print(f"Connected: {gen.idn()}")
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    print("\n--- Testing PWM Logic Signal ---")
    # Generate a 0V to 5V digital signal (TTL)
    # 5Vpp Amplitude + 2.5V Offset = 0V to 5V swing
    
    print("Configuring: 1kHz Square, 20% Duty, 0-5V Logic Levels")
    gen.configure_pwm(freq=1000, vpp=5.0, duty_cycle=20, offset=2.5)
    
    # Ensure impedance is set to High-Z if you are just measuring with a scope probe
    gen.set_output_impedance("HZ") 
    
    gen.output_on()
    print("Output is ON. Check Scope for a narrow pulse!")
    
    # Keep on for 10 seconds then shut down
    time.sleep(10)
    
    gen.output_off()
    print("Output is OFF.")

if __name__ == "__main__":
    main()