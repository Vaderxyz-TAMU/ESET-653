from bench.visa_manager import VisaManager
from bench.instrument_setup import instrument_factory 

def connect_all():
    vm = VisaManager()
    devices = {}

    print("Scanning for instruments...")

    for res in vm.list_resources():
        inst = None
        try:
            # Open the raw connection
            inst = vm.open(res)
            
            # Attempt to identify and create the specific device object
            dev = instrument_factory(inst)
            
            # FIX: Use the unique resource ID (res) as the key.
            # This allows multiple instruments of the same type to exist in the dict.
            devices[res] = dev
            
            # Optional: Print success message for feedback
            print(f"Successfully connected: {type(dev).__name__} at {res}")

        except Exception as e:
            # Error Handling: Catch unsupported instruments or connection timeouts
            print(f"Skipping resource {res}: {e}")
            
            # Cleanup: If we opened the connection but couldn't use it, close it.
            if inst:
                try:
                    inst.close()
                except:
                    pass

    return devices