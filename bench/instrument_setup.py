from bench.instruments.DMM import Agilent34401A
from bench.instruments.PSU import AgilentE363x
from bench.instruments.AWG import BK40XXB
from bench.instruments.OSCOPE import TektronixScope

def instrument_factory(inst):
    idn = inst.query("*IDN?")

    if "34401" in idn:
        return Agilent34401A(inst)

    if "E363" in idn:
        return AgilentE363x(inst)

    if "BK" in idn and ("05" in idn or "06" in idn):
        return BK40XXB(inst)

    if "TEKTRONIX" in idn and ("DPO" in idn or "MSO" in idn):
        return TektronixScope(inst)

    raise RuntimeError(f"Unsupported instrument: {idn}")
