"""
This file contains the functions necessary for
connecting and sending triggers to an EEG system.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025, using code by Ezra Nasrawi
"""

import serial
from psychopy import core

class EEG:
    """
    usage:

       from EEG import EEG

    To initialise:

       eeg = EEG([port])
    """

    def __init__(self, port_address) -> None:
        """
        This connects to the EEG.
        """
        self.port = serial.Serial(port_address, baudrate=115200)

    def send_trigger(self, trigger):
        self.port.write(bytes([trigger]))

    def stop(self):
        self.port.close()