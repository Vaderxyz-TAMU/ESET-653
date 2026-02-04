from bench.base_scpi import SCPIDevice

class BK40XXB(SCPIDevice):
    """
    Robust Driver for BK Precision 4050B / 4060B Series.
    Command Reference: C1:BSWV <Parameter>,<Value>
    """

    def set_waveform(self, shape, channel=1):
        """
        Shape options: SINE, SQUARE, RAMP, PULSE, NOISE, DC
        """
        shape = shape.upper()
        # FIX: Changed 'TYPE' to 'WVTP' to match your working Lab 1 code
        self.write(f"C{channel}:BSWV WVTP,{shape}")

    def set_frequency(self, freq, channel=1):
        """Sets frequency in Hz."""
        self.write(f"C{channel}:BSWV FRQ,{freq}")

    def set_amplitude(self, amp_vpp, channel=1):
        """Sets Amplitude in Vpp (Peak-to-Peak)."""
        self.write(f"C{channel}:BSWV AMP,{amp_vpp}")

    def set_offset(self, offset_volts, channel=1):
        """
        Sets DC Offset in Volts.
        """
        self.write(f"C{channel}:BSWV OFST,{offset_volts}")

    def set_phase(self, degrees, channel=1):
        """Sets phase in degrees (0-360)."""
        self.write(f"C{channel}:BSWV PHSE,{degrees}")

    def set_duty_cycle(self, percent, channel=1):
        """
        Sets Duty Cycle for SQUARE waves (0.1% to 99.9%).
        Only works if waveform is currently SQUARE.
        """
        self.write(f"C{channel}:BSWV DUTY,{percent}")

    def set_symmetry(self, percent, channel=1):
        """
        Sets Symmetry for RAMP waves (0% to 100%).
        50% = Triangle, 0% or 100% = Sawtooth.
        """
        self.write(f"C{channel}:BSWV SYMM,{percent}")

    def set_output_impedance(self, load="50", channel=1):
        """
        Set '50' for 50 Ohm matching (standard).
        Set 'HZ' for High-Z (multimeter/scope measuring without termination).
        """
        self.write(f"C{channel}:OUTP LOAD,{load}")

    def output_on(self, channel=1):
        self.write(f"C{channel}:OUTP ON")

    def output_off(self, channel=1):
        self.write(f"C{channel}:OUTP OFF")

    # --- Convenience Helpers ---

    def configure_sine(self, freq, vpp, offset=0, channel=1):
        """One-shot setup for a standard Sine wave."""
        self.set_waveform("SINE", channel)
        self.set_frequency(freq, channel)
        self.set_amplitude(vpp, channel)
        self.set_offset(offset, channel)

    def configure_pwm(self, freq, vpp, duty_cycle=50, offset=0, channel=1):
        """One-shot setup for a PWM/Square wave."""
        self.set_waveform("SQUARE", channel)
        self.set_frequency(freq, channel)
        self.set_amplitude(vpp, channel)
        self.set_offset(offset, channel)
        self.set_duty_cycle(duty_cycle, channel)