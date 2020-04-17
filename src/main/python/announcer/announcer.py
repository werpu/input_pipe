import socket
import json
import threading
from subprocess import check_output


class Announcer:

    def __init__(self, udp_host='192.168.0.1', udp_port=5000, server_port="9001"):
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.host_name = socket.gethostname()
        self.host_port = server_port
        self.host_ip = check_output(['hostname', '-I'])

        # socket.gethostbyname(self.host_name)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def announce(self):
        msg_json = {
                  "msg": "pipe_location",
                  "ip": str(self.host_ip, 'UTF-8').split(" ")[0],
                  "port": self.host_port
              }
        msg = json.dumps(msg_json)

        b = bytearray()
        b.extend(map(ord, msg))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.sendto(b, ('255.255.255.255', 12345))

    def run(self):
        self.announce()
        threading.Timer(5, self.run).start()

    def start(self):
        self.run()

