#!/usr/bin/env python
import os
import sys
import time
import subprocess

def log(text):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print("{timestamp}: {message}".format(timestamp = timestamp, message = text))

class Application():
    def __init__(self, app_dir, app_cmd):
        self.app_dir = app_dir
        self.app_cmd = app_cmd
        self.process = None

    def start(self):
        log("Starting new instance in {self.app_dir}".format(**locals()))
        log("Command {self.app_cmd}".format(**locals()))
        cwd = os.getcwd()
        os.chdir(self.app_dir)
        process = subprocess.Popen(self.app_cmd)
        log("Started pid {process.pid}".format(**locals()))
        os.chdir(cwd)
        return process

    def stop(self):
        log("Terminating pid {self.process.pid}".format(**locals()))
        self.process.terminate()
        time.sleep(3)
        return None

    def restart(self):
        if self.process:
            self.process = self.stop()
        self.process = self.start()

