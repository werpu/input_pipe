####
# message receiver
# for running updates during
# runtime
####
# thanks to https://steelkiwi.com/blog/working-tcp-sockets/ for the excellent tuorial

import asyncio
from asyncio import ReadTransport

from pymitter import EventEmitter


class EventProtocol(asyncio.Protocol):

    transport: ReadTransport = None

    def __init__(self, q, e):
        self.q = q
        self.event_emitter = e

    def connection_made(self, transport: ReadTransport):
        self.transport = transport

    def data_received(self, data):
        self.q.put(data)
        self.event_emitter.emit("data_available")


class Receiver:

    def __init__(self, *args, **kwargs):
        self.queue = kwargs.pop("__queue")
        self.event_emitter = EventEmitter()

    def on(self, event_str, lambda_func):
        self.event_emitter.on(event_str, lambda: lambda_func())

    async def start(self, port):
        q = self.queue
        e = self.event_emitter
        # look at all network interfaces
        await (asyncio.get_event_loop()).create_server(protocol_factory=lambda: EventProtocol(q, e), host=None, port=port)

