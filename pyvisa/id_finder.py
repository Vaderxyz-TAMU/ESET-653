import pyvisa
from dataclasses import dataclass

def list_visa_resources() -> list[str]:
    rm = pyvisa.ResourceManager()
    return list(rm.list_resources())

@dataclass(frozen=True)
class InstrumentId:
    vendor: str
    model: str
    serial: str | None
    raw_idn: str

def safe_idn(rm, resource: str, timeout_ms=800) -> InstrumentId | None:
    try:
        inst = rm.open_resource(resource)
        inst.timeout = timeout_ms
        inst.write_termination = "\n"
        inst.read_termination = "\n"
        idn = inst.query("*IDN?").strip()
        inst.close()

        parts = [p.strip() for p in idn.split(",")]
        vendor = parts[0] if len(parts) > 0 else "UNKNOWN"
        model  = parts[1] if len(parts) > 1 else "UNKNOWN"
        serial = parts[2] if len(parts) > 2 and parts[2] else None
        return InstrumentId(vendor, model, serial, idn)
    except Exception:
        return None

print(list_visa_resources())
