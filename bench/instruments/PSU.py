from bench.base_scpi import SCPIDevice

class AgilentE363x(SCPIDevice):
    def select_output(self, output):
        self.write(f"INST:SEL {output}")  # P6V, P25V, N25V

    def set_voltage(self, voltage):
        self.write(f"VOLT {voltage}")

    def set_current(self, current):
        self.write(f"CURR {current}")

    def output_on(self):
        self.write("OUTP ON")

    def output_off(self):
        self.write("OUTP OFF")
