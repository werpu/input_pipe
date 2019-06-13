####
# message receiver
# for running updates during
# runtime
####
from circuits.net.sockets import TCPClient


class Sender:

    def __init__(self, port=8000):
        self.port = port
        self.client = None

    def open(self):
        self.client = TCPClient(bind=("localhost", self.port))

    def send_message(self, msg):
        self.client.write(msg)

    def close(self):
        self.client.close()

