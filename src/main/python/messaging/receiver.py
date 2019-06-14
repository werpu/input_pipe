####
# message receiver
# for running updates during
# runtime
####

from circuits.net.sockets import TCPServer
from circuits import Event, ipc
from circuits import Component, handler


class tcp_result(Event):

    def __init__(self,  *args, **kwargs):
        Event.__init__(self, *args, **kwargs)

    """tcp_result Event"""


class Receiver(TCPServer):

    def __init__(self,  *args, **kwargs):
        self.queue = kwargs.pop("__queue")
        TCPServer.__init__(self, *args, **kwargs)

    @handler("read")
    def on_read(self, sock, data):
        self.queue.put(data)





