import pyudev

#class UdevListener:

context = pyudev.Context()

for device in context.list_devices(subsystem='input'):
    if device.get("ID_MODEL_ID") == "0410":
        print(device.get("ID_VENDOR_ID"))
        print(device.get("ID_MODEL_ID"))
        print(device.device_type)


