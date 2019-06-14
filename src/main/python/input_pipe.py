# MIT License
#
# Copyright (c) 2019 Werner Punz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
# https://python-evdev.readthedocs.io/en/latest/usage.html
import asyncio
import uvloop
from pidfile import PIDFile
from ev_core.config import Config
from ev_core.event_loop import EventController
from messaging.sender import Sender
from messaging.receiver import Receiver
from queue import Queue
import sys

class MainApp:

    def __init__(self):

        parser = argparse.ArgumentParser(description='Point to the yaml config')

        parser.add_argument('--server', "-s",
                            dest='server',
                            default="Y",
                            help='run inputpipe as server (default Y)')

        parser.add_argument('--config', "-c",
                            dest='conf',
                            default="./devices.yaml",
                            help='define a config file location (default: ./devices.yaml)')

        parser.add_argument('--pidfile', "-pd",
                            dest='pidfile',
                            default="/tmp/input_pipe.pid",
                            help='define a pid file location (default: /tmp/input_pipe.pid')

        parser.add_argument('--port', "-p",
                            dest='port',
                            default="-1",
                            help='communications port for the input_pipe (default -1), -1 disables the command server, for security reasons the server is disabled per default')

        parser.add_argument('--command', "-cm",
                            dest='command',
                            default="reload",
                            help='command for the server (default: reload')

        self.args = parser.parse_args()
        self.msg_queue = Queue()
        port = int(self.args.port)
        if port > -1:
            self.receiver = Receiver(bind=("localhost", 9001), __queue=self.msg_queue)
        else:
            self.receiver = None
        self.config = None
        self.evtcl = None

    # Central event dispatcher
    # which dispatches the events coming in from the event loop
    # to their taevtergets
    async def event_dispatch(self):
        while True:
            if self.msg_queue.qsize() > 0:
                item = self.msg_queue.get()
                msg = item.decode('utf-8').strip()
                if msg == "reload":
                    self.evtcl.reload()
                if msg == "stop":
                    self.evtcl.stop()
                    asyncio.get_event_loop().stop()
                    sys.exit(0)

            else:
                await asyncio.sleep(5)

    def run(self):
        if self.args.server == "Y":
            uvloop.install()
            self.init_server()
            self.run_pid()
        else:
            self.send_command()

    def send_command(self):
        sender = Sender("localhost", self.args.port)
        try:
            sender.open()
            sender.send_message(self.args.command)
        finally:
            sender.close()

    def init_server(self):
        if self.receiver is None:
            return

        print("starting command server on port: 9001")
        self.receiver.start()
        print("command server started")

    def run_pid(self):
        with PIDFile(self.args.pidfile):
            self.config = Config(self.args.conf)
            asyncio.ensure_future(self.event_dispatch())
            self.evtcl = EventController(self.config)
            asyncio.get_event_loop().run_forever()


MainApp().run()

