

# a basic device mockup
class DeviceMock:

    def __init__(self, path="", info=[], name="", phys="", uniq="", version=""):
        self.path = path
        self.info = info  # bustype, vendor, product, version
        self.name = name
        self.phys = phys
        self.uniq = uniq
        self.version = version



