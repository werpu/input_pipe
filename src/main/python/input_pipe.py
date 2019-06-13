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
from circuits import Component, handler


class MainApp(Component):

    args = None
    receiver = None

    def init(self):

        parser = argparse.ArgumentParser(description='Point to the yaml config')

        parser.add_argument('--server', "-s",
                            dest='server',
                            default="N",
                            help='run inputpipe as server (default N)')

        parser.add_argument('--config', "-c",
                            dest='conf',
                            default="./devices.yaml",
                            help='define a config file location (default: ./devices.yaml)')

        parser.add_argument('--pidfile', "-pd",
                            dest='pidfile',
                            default="/tmp/input_pipe2.pid",
                            help='define a pid file location (default: /tmp/input_pipe.pid')

        parser.add_argument('--port', "-p",
                            dest='port',
                            default="9001",
                            help='communications port for the input_pipe (default 9001), -1 disables the server')

        parser.add_argument('--command', "-cm",
                            dest='command',
                            default="reload",
                            help='command for the server (default: reload')

        self.args = parser.parse_args()

        self.receiver = Receiver(bind=("localhost", 9001))
        self.register(self.receiver)

    @handler("tcp_result", channel="*")
    def on_tcp_result(self, *args, **kwargs):
        print(kwargs["value"].decode('utf-8'))

    def started(self, component):
        if component == self.receiver:
            return

        def send_command():
            sender = Sender("localhost", self.args.port)
            sender.open()
            sender.send_message(self.args.command)

        if self.args.server == "Y":
            uvloop.install()

            self.init_server()
            self.initController()

        else:
            send_command()

    def init_server(self):
        print("starting command server on port: 9001")
        self.receiver.start(process=True, link=self)
        print("command server started")

    def initController(self):
        with PIDFile(self.args.pidfile):
            EventController(Config(self.args.conf))
            asyncio.get_event_loop().run_forever()


class App(Component):

    def init(self):
        MainApp().register(self)


App().run()

