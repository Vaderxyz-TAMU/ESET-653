from bench.base_scpi import SCPIDevice

class TektronixScope(SCPIDevice):
    def autoset(self):
        self.write("AUTOS EXEC")

    def set_channel_on(self, ch):
        self.write(f"SEL:{ch} ON")

    def measure_vpp(self, ch):
        self.write("MEASU:MEAS1:TYPE PK2PK")
        self.write(f"MEASU:MEAS1:SOUR {ch}")
        return float(self.query("MEASU:MEAS1:VAL?"))
