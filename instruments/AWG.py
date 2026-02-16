import pyvisa
import time

class AWG:
    def __init__(self, resource_string):
        self.rm = pyvisa.ResourceManager()
        self.gen = self.rm.open_resource(resource_string)

        # configure timeout
        self.gen.timeout = 10000

        # Verify and Initialize
        idn = self.gen.query("*IDN?")
        print(f"Connected to: {idn.strip()}")
        
        self.gen.write("*RST")
        self.gen.write("*CLS")
    
    # [cite_start]--- Common Commands --- [cite: 334]

    def reset(self):
        """Initiates a device reset to factory default settings."""
        self.gen.write("*RST")

    def operation_complete(self):
        """Returns '1' when all pending operations are finished."""
        return self.gen.query("*OPC?")

    def wait(self):
        """Sets the Operation Complete bit after all pending commands are completed."""
        self.gen.write("*OPC")

    # [cite_start]--- Output Commands --- [cite: 363]

    def set_output(self, channel=1, enabled=True):
        """
        Enables or disables the output of the selected channel.
        awg.enable_output(1, True) - Channel 1 Output ON
        """
        state = "ON" if enabled else "OFF"
        self.gen.write(f"C{channel}:OUTPut {state}")

    def set_output_load(self, channel=1, load=50):
        """
        Sets the output load.
        load: 50 to 100000 (Ohms) or 'HZ' (High Impedance)
        """
        self.gen.write(f"C{channel}:OUTPut LOAD, {load}")

    def set_output_polarity(self, channel=1, inverted=False):
        """
        Sets the output polarity.
        inverted: True for Inverted, False for Normal
        """
        polarity = "INVT" if inverted else "NOR"
        self.gen.write(f"C{channel}:OUTPut PLRT, {polarity}")
    
    def add_noise(self, channel=1, enabled=True, ratio=120):
        """
        Adds noise to the output.
        ratio: Signal-to-noise ratio
        """
        state = "ON" if enabled else "OFF"
        self.gen.write(f"C{channel}:NOISE_ADD STATE, {state}, RATIO, {ratio}")

    # [cite_start]--- Basic Waveform Commands (BSWV) --- [cite: 377]

    def set_sine_wave(self, frequency=1000, amplitude=1.0, offset=0.0, channel=1):
        """
        Sets a sine wave on the specified channel.
        awg.set_sine_wave(1000, 5, 1, 1) - Sine, 1kHz, 5Vpp, 1V Offset, CH1
        """
        self.gen.write(f'C{channel}:BaSic_WaVe WVTP, SINE')
        self.gen.write(f'C{channel}:BaSic_WaVe FRQ, {frequency}')
        self.gen.write(f'C{channel}:BaSic_WaVe AMP, {amplitude}')
        self.gen.write(f'C{channel}:BaSic_WaVe OFST, {offset}')

    def set_square_wave(self, frequency=1000, amplitude=1.0, offset=0.0, duty_cycle=50, channel=1):
        """
        Sets a square wave on the specified channel.
        awg.set_square_wave(1000, 5, 0, 50, 1) - Square, 1kHz, 5Vpp, 50% Duty, CH1
        """
        self.gen.write(f'C{channel}:BaSic_WaVe WVTP, SQUARE')
        self.gen.write(f'C{channel}:BaSic_WaVe FRQ, {frequency}')
        self.gen.write(f'C{channel}:BaSic_WaVe AMP, {amplitude}')
        self.gen.write(f'C{channel}:BaSic_WaVe OFST, {offset}')
        self.gen.write(f'C{channel}:BaSic_WaVe DUTY, {duty_cycle}')

    def set_ramp_wave(self, frequency=1000, amplitude=1.0, offset=0.0, symmetry=50, channel=1):
        """
        Sets a ramp/triangle wave on the specified channel.
        symmetry: 0 to 100%
        """
        self.gen.write(f'C{channel}:BaSic_WaVe WVTP, RAMP')
        self.gen.write(f'C{channel}:BaSic_WaVe FRQ, {frequency}')
        self.gen.write(f'C{channel}:BaSic_WaVe AMP, {amplitude}')
        self.gen.write(f'C{channel}:BaSic_WaVe OFST, {offset}')
        self.gen.write(f'C{channel}:BaSic_WaVe SYM, {symmetry}')

    def set_pulse_wave(self, frequency=1000, amplitude=1.0, offset=0.0, width=1e-3, rise=8.4e-9, fall=8.4e-9, channel=1):
        """
        Sets a pulse wave on the specified channel.
        width, rise, fall: in Seconds
        """
        self.gen.write(f'C{channel}:BaSic_WaVe WVTP, PULSE')
        self.gen.write(f'C{channel}:BaSic_WaVe FRQ, {frequency}')
        self.gen.write(f'C{channel}:BaSic_WaVe AMP, {amplitude}')
        self.gen.write(f'C{channel}:BaSic_WaVe OFST, {offset}')
        self.gen.write(f'C{channel}:BaSic_WaVe WIDTH, {width}')
        self.gen.write(f'C{channel}:BaSic_WaVe RISE, {rise}')
        self.gen.write(f'C{channel}:BaSic_WaVe FALL, {fall}')

    def set_noise_wave(self, stdev=0.5, mean=0.0, bandwidth_state="OFF", bandwidth_val=20e6, channel=1):
        """
        Sets a noise waveform.
        stdev: Standard deviation (V)
        bandwidth_val: Bandwidth in Hz (if state is ON)
        """
        self.gen.write(f'C{channel}:BaSic_WaVe WVTP, NOISE')
        self.gen.write(f'C{channel}:BaSic_WaVe STDEV, {stdev}')
        self.gen.write(f'C{channel}:BaSic_WaVe MEAN, {mean}')
        self.gen.write(f'C{channel}:BaSic_WaVe BANDSTATE, {bandwidth_state}')
        if bandwidth_state == "ON":
            self.gen.write(f'C{channel}:BaSic_WaVe BANDWIDTH, {bandwidth_val}')

    def set_dc_wave(self, offset=0.0, channel=1):
        """
        Sets a DC voltage level.
        """
        self.gen.write(f'C{channel}:BaSic_WaVe WVTP, DC')
        self.gen.write(f'C{channel}:BaSic_WaVe OFST, {offset}')

    def set_arb_wave(self, frequency=1000, amplitude=1.0, offset=0.0, channel=1):
        """
        Sets the channel to output the currently loaded Arbitrary waveform.
        """
        self.gen.write(f'C{channel}:BaSic_WaVe WVTP, ARB')
        self.gen.write(f'C{channel}:BaSic_WaVe FRQ, {frequency}')
        self.gen.write(f'C{channel}:BaSic_WaVe AMP, {amplitude}')
        self.gen.write(f'C{channel}:BaSic_WaVe OFST, {offset}')

    # [cite_start]--- Modulation Commands (MDWV) --- [cite: 94]

    def set_modulation_state(self, channel=1, enabled=True):
        """Enables or disables modulation."""
        state = "ON" if enabled else "OFF"
        self.gen.write(f'C{channel}:MoDulateWaVe STATE, {state}')

    def set_modulation_type(self, mod_type="AM", channel=1):
        """
        Sets modulation type.
        mod_type: AM, FM, PM, FSK, ASK, PSK, PWM, DSBAM
        """
        self.gen.write(f'C{channel}:MoDulateWaVe {mod_type}')

    def set_modulation_source(self, mod_type="AM", source="INT", channel=1):
        """
        Sets modulation source to Internal (INT) or External (EXT).
        """
        self.gen.write(f'C{channel}:MoDulateWaVe {mod_type}, SRC, {source}')

    def set_modulation_internal_shape(self, mod_type="AM", shape="SINE", channel=1):
        """
        Sets the internal modulating wave shape.
        shape: SINE, SQUARE, TRIANGLE, UPRAMP, DNRAMP, NOISE, ARB
        """
        self.gen.write(f'C{channel}:MoDulateWaVe {mod_type}, MDSP, {shape}')

    def set_modulation_frequency(self, mod_type="AM", frequency=100, channel=1):
        """Sets the frequency of the modulating signal (Internal source)."""
        self.gen.write(f'C{channel}:MoDulateWaVe {mod_type}, FRQ, {frequency}')

    def set_am_depth(self, depth=100, channel=1):
        """Sets AM modulation depth (0 to 120%)."""
        self.gen.write(f'C{channel}:MoDulateWaVe AM, DEPTH, {depth}')

    def set_fm_deviation(self, deviation=1000, channel=1):
        """Sets FM frequency deviation."""
        self.gen.write(f'C{channel}:MoDulateWaVe FM, DEVI, {deviation}')

    # [cite_start]--- Sweep Commands (SWWV) --- [cite: 139]

    def set_sweep_state(self, channel=1, enabled=True):
        """Enables or disables sweep mode."""
        state = "ON" if enabled else "OFF"
        self.gen.write(f'C{channel}:SweepWaVe STATE, {state}')

    def set_sweep_time(self, time=1.0, channel=1):
        """Sets the sweep duration in seconds."""
        self.gen.write(f'C{channel}:SweepWaVe TIME, {time}')

    def set_sweep_range(self, start_freq=100, stop_freq=1000, channel=1):
        """Sets the start and stop frequencies for the sweep."""
        self.gen.write(f'C{channel}:SweepWaVe START, {start_freq}')
        self.gen.write(f'C{channel}:SweepWaVe STOP, {stop_freq}')

    def set_sweep_mode(self, mode="LINE", channel=1):
        """
        Sets sweep mode.
        mode: LINE (Linear) or LOG (Logarithmic)
        """
        self.gen.write(f'C{channel}:SweepWaVe SWMD, {mode}')

    def set_sweep_direction(self, direction="UP", channel=1):
        """
        Sets sweep direction.
        direction: UP or DOWN
        """
        self.gen.write(f'C{channel}:SweepWaVe DIR, {direction}')

    def set_sweep_trigger(self, source="INT", channel=1):
        """
        Sets sweep trigger source.
        source: INT, EXT, MAN (Manual)
        """
        self.gen.write(f'C{channel}:SweepWaVe TRSR, {source}')

    def manual_sweep_trigger(self, channel=1):
        """Manually triggers a sweep (if source is MAN)."""
        self.gen.write(f'C{channel}:SweepWaVe MTRIG')

    # [cite_start]--- Burst Commands (BTWV) --- [cite: 165]

    def set_burst_state(self, channel=1, enabled=True):
        """Enables or disables burst mode."""
        state = "ON" if enabled else "OFF"
        self.gen.write(f'C{channel}:BurstWaVe STATE, {state}')

    def set_burst_period(self, period=10e-3, channel=1):
        """Sets the burst period in seconds (for internal trigger)."""
        self.gen.write(f'C{channel}:BurstWaVe PRD, {period}')

    def set_burst_cycles(self, cycles=1, channel=1):
        """Sets the number of cycles per burst."""
        self.gen.write(f'C{channel}:BurstWaVe TIME, {cycles}') # Note: Manual uses 'TIME' keyword for cycles in some contexts, or 'CYC' check specific firmware. Based on manual context often TIME is used for cycle count in NCYC mode.
        # If 'TIME' is strictly time, use 'CYC' parameter if available or verify specific command syntax for cycle count often 'TIME' in burst context sets cycle count for N-Cycle mode.
        # Correction based on standard SCPI for this unit:
        self.gen.write(f'C{channel}:BurstWaVe TIME, {cycles}') 

    def set_burst_mode(self, mode="NCYC", channel=1):
        """
        Sets burst mode.
        mode: NCYC (N-Cycle), GATED, INF (Infinite)
        """
        self.gen.write(f'C{channel}:BurstWaVe GATE_NCYC, {mode}')

    def set_burst_trigger(self, source="INT", channel=1):
        """
        Sets burst trigger source.
        source: INT, EXT, MAN
        """
        self.gen.write(f'C{channel}:BurstWaVe TRSR, {source}')

    # --- Utility and System ---

    def close(self):
        # Turn off all outputs
        self.gen.close()
        self.rm.close()