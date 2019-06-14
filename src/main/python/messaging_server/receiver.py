####
# message receiver
# for running updates during
# runtime
####
import asyncio


class EventProtocol(asyncio.Protocol):

    def __init__(self, q):
        self.q = q

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.q.put(data)


class Receiver:

    def __init__(self, *args, **kwargs):
        self.queue = kwargs.pop("__queue")

    async def start(self, port):
        q = self.queue

        await (asyncio.get_event_loop()).create_server(protocol_factory=lambda: EventProtocol(q), host="localhost", port=port)

