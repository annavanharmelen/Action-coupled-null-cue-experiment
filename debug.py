"""
This script is used to test random aspects
of the 'action coupled null-cue' experiment.

made by Anna van Harmelen, 2025
"""
from trial import generate_stimuli_characteristics
from set_up import get_settings
from practice import practice

testing = True

monitor = {
            "resolution": (1920, 1080),  # in pixels
            "Hz": 60,  # screen refresh rate in Hz
            "width": 33,  # in cm
            "distance": 50,  # in cm
        }

directory = r"../../Testing/"
settings = get_settings(monitor, directory, "red")

practice(testing, "red", settings)
