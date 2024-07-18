import os
import sys
import shutil
import re
import time
import threading
from setuptools import setup, find_packages
from setuptools import  Command
from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from datetime import datetime
import logging

class Spinner:
    def __init__(self, message="Loading"):
        self.message = message
        self.spinning = False
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.spinner_thread = None

    def spin(self):
        while self.spinning:
            for char in self.spinner_chars:
                sys.stdout.write(f'\r{char} {self.message}')
                sys.stdout.flush()
                time.sleep(0.1)

    def start(self):
        self.spinning = True
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.start()

    def stop(self):
        self.spinning = False
        if self.spinner_thread:
            self.spinner_thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

    def update_message(self, new_message):
        self.message = new_message
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()
