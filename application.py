#!/usr/bin/env python
import os
import sys
import time
import signal
import subprocess

def log(text):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print("{timestamp}: {message}".format(timestamp = timestamp, message = text))

from contextlib import contextmanager
@contextmanager
def temp_chdir(temp_dir):
    curr_dir = os.getcwd()
    os.chdir(temp_dir)
    yield
    os.chdir(curr_dir)

class Application():
    def __init__(self, app_dir, app_cmd, app_init):
        self.app_dir = app_dir
        self.app_cmd = app_cmd
        self.app_init = app_init
        self.process = None

    def init(self):
        if not self.app_init:
            return None
        log("Initializing instance in {self.app_dir}".format(**locals()))
        log("Command {self.app_init}".format(**locals()))
        with temp_chdir(self.app_dir):
            subprocess.call(self.app_init, shell=True)

    def start(self):
        log("Starting new instance in {self.app_dir}".format(**locals()))
        log("Command {self.app_cmd}".format(**locals()))
        with temp_chdir(self.app_dir):
            process = subprocess.Popen(self.app_cmd, preexec_fn=os.setsid, shell=True)
        log("Started pid {process.pid}".format(**locals()))
        return process

    def stop(self):
        log("Terminating pid {self.process.pid}".format(**locals()))
        os.killpg(self.process.pid, signal.SIGTERM)
        return None

    def restart(self):
        if self.process:
            self.process = self.stop()
        self.process = self.start()

    def run(self, app_dir, app_cmd):
        return process

