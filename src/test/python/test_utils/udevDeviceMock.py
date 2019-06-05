from utils.langutils import to_camel_case


# A simple udev device mock needed to mock
# the device parts of the udev system we touch here
class UdevDeviceMock:
    def __init__(self, idVendor, idModel, idVendorId = "", idModelId = ""):
        self.idVendor = idVendor
        self.idModel = idModel
        self.idVendorId = idVendorId
        self.idModelId = idModelId

    def get(self, key):
        return self.__getattribute__(to_camel_case(key.lower()))
