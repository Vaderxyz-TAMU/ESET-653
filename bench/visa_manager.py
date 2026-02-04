import pyvisa

class VisaManager:
    def __init__(self, backend=''):
        self.rm = pyvisa.ResourceManager(backend)

    def list_resources(self):
        return self.rm.list_resources()

    def open(self, resource_name, timeout=5000):
        inst = self.rm.open_resource(resource_name)
        inst.timeout = timeout
        inst.write_termination = '\n'
        inst.read_termination = '\n'
        return inst
