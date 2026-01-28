from bench.instruments.dmm_34401a import Agilent34401A
from bench.instruments.psu_e363x import AgilentE363x
from bench.instruments.funcgen_bk4050 import BK4050
from bench.instruments.scope_tektronix import TektronixScope

def instrument_factory(inst):
    idn = inst.query("*IDN?")

    if "34401" in idn:
        return Agilent34401A(inst)

    if "E363" in idn:
        return AgilentE363x(inst)

    if "BK" in idn and "405" in idn:
        return BK4050(inst)

    if "TEKTRONIX" in idn and ("DPO" in idn or "MSO" in idn):
        return TektronixScope(inst)

    raise RuntimeError(f"Unsupported instrument: {idn}")
