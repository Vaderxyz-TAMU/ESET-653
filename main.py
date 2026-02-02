from datetime import datetime
from bench import connect_all
from bench.csv_logger import CSVLogger

devices = connect_all()

dmm = devices["Agilent34401A"]
psu = devices["AgilentE363x"]
fg = devices["BK4050"]
scope = devices["TektronixScope"]

psu.select_output("P6V")
psu.set_voltage(5.0)
psu.set_current(1.0)
psu.output_on()

fg.set_waveform("SIN")
fg.set_frequency(1_000)
fg.set_amplitude_vpp(4.0)
fg.output_on()

record = {
    "timestamp": datetime.utcnow().isoformat(),
    "dmm_voltage_v": dmm.measure_voltage(),
    "psu_voltage_set_v": 5.0,
    "psu_current_set_a": 1.0,
    "funcgen_freq_hz": 1_000,
    "scope_vpp_v": scope.measure_vpp("CH1"),
}

logger = CSVLogger("data/bench_log.csv", record.keys())
logger.write_row(record)

print("Logged:", record)
