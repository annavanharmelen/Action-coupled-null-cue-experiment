"""
This file contains the functions necessary for
connecting and sending triggers to an EEG system.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025, using code by Ezra Nasrawi
"""

from psychopy import serial


class EEG:
    """
    usage:

       from EEG import EEG

    To initialise:

       eeg = EEG([port])
    """

    def __init__(self, port) -> None:
        """
        This connects to the EEG.
        """
        portEEG = serial.Serial(port)

        return portEEG

    def send_trigger(self, trigger):
        self.write(str.encode(trigger))
