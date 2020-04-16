####
# message receiver
# for running updates during
# runtime
####
# thanks to https://steelkiwi.com/blog/working-tcp-sockets/ for the excellent tuorial

import asyncio
from asyncio import ReadTransport


class EventProtocol(asyncio.Protocol):

    transport: ReadTransport = None

    def __init__(self, q):
        self.q = q

    def connection_made(self, transport: ReadTransport):
        self.transport = transport

    def data_received(self, data):
        self.q.put(data)


class Receiver:

    def __init__(self, *args, **kwargs):
        self.queue = kwargs.pop("__queue")

    async def start(self, port):
        q = self.queue
        # look at all network interfaces
        await (asyncio.get_event_loop()).create_server(protocol_factory=lambda: EventProtocol(q), host=None, port=port)

