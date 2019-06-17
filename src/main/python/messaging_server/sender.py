####
# message receiver
# for running updates during
# runtime
####
import asyncio

from asyncio import WriteTransport


class SenderProtocol(asyncio.Protocol):

    def __init__(self, message):
        self.message  = message

    def connection_made(self, transport: WriteTransport):
        transport.write(self.message.encode())
        transport.close()


class Sender:

    def __init__(self, port):
        self.port = port

    def send_message(self, msg):
        conn = asyncio.get_event_loop().create_connection(lambda: SenderProtocol(msg), "localhost", self.port)
        asyncio.get_event_loop().run_until_complete(conn)
        conn.close()



