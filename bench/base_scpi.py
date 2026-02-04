class SCPIDevice:
    def __init__(self, inst):
        self.inst = inst

    def write(self, cmd):
        self.inst.write(cmd)

    def query(self, cmd):
        return self.inst.query(cmd)

    def idn(self):
        return self.query("*IDN?")

    def reset(self):
        self.write("*RST")

    def close(self):
        self.inst.close()
    
    # ... existing init ...
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
