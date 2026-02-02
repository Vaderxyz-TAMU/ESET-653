from bench.visa_manager import VisaManager
from bench.instrument_factory import instrument_factory

def connect_all():
    vm = VisaManager()
    devices = {}

    for res in vm.list_resources():
        inst = vm.open(res)
        dev = instrument_factory(inst)
        devices[type(dev).__name__] = dev

    return devices
