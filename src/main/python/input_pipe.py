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

        parser.add_argument('--pidfile', "-p",
                            dest='pidfile',
                            default="/tmp/input_pipe2.pid",
                            help='define a pid file location (default: /tmp/input_pipe.pid')

        parser.add_argument('--remotekey', "-r",
                            dest='remote_key',
                            default="input_pipe",
                            help='remote key for remote control functions, change only, ' +
                                 'if you run multiple instances (default: input_pipe)')

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

        def initController():

            with PIDFile(self.args.pidfile):
                EventController(Config(self.args.conf))
                asyncio.get_event_loop().run_forever()

        def send_command():
            sender = Sender(self.args.remote_key)
            sender.open()
            sender.send_message(self.args.command)

        if self.args.server == "Y":
            uvloop.install()

            print("starting command server on port: 9001")
            self.receiver.start(process=True, link=self)
            print("command server started")
            initController()

        else:
            send_command()


class App(Component):

    def init(self):
        MainApp().register(self)


App().run()

