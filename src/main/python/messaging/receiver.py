####
# message receiver
# for running updates during
# runtime
####


from circuits import handler
from circuits.net.sockets import TCPServer
from circuits import Event, ipc
from circuits import Component, handler


class tcp_result(Event):

    def __init__(self,  *args, **kwargs):
        Event.__init__(self, *args, **kwargs)

    """tcp_result Event"""


class Receiver(TCPServer):

    def __init__(self,  *args, **kwargs):
        TCPServer.__init__(self, *args, **kwargs)

    @handler("read")
    def on_read(self, sock, data):
        self.fire(ipc(tcp_result(value=data)), "*")


##
# asyncio helper to push this one into the background
##
def start_receiver(port=8001):
    print("starting command server on port: " + port.__str__())
    final_port = port or 8001
    Receiver(bind=("localhost", final_port)).start(process=True)
    print("command server started")


class App(Component):
    def started(self, component):
        start_receiver()


##App().run()



