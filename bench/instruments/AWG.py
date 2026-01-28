from bench.base_scpi import SCPIDevice

class BK4050(SCPIDevice):
    def set_waveform(self, shape, channel=1):
        self.write(f"SOUR{channel}:FUNC {shape}")

    def set_frequency(self, freq, channel=1):
        self.write(f"SOUR{channel}:FREQ {freq}")

    def set_amplitude_vpp(self, amp, channel=1):
        self.write(f"SOUR{channel}:VOLT {amp}")

    def output_on(self, channel=1):
        self.write(f"OUTP{channel} ON")

    def output_off(self, channel=1):
        self.write(f"OUTP{channel} OFF")
