import evdev


class EvDevUtils:

    # externalized producer to be replaced in testing cases by mocks
    @staticmethod
    def get_available_devices():
        return [evdev.InputDevice(path) for path in evdev.list_devices()]

