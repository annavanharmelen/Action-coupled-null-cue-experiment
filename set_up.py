"""
This file contains the functions necessary for
seting up the computer.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual
from psychopy.hardware.keyboard import Keyboard
from math import degrees, atan2, pi
import random

# COLOURS = blue, pink, green, orange
# COLOURS = [[19, 146, 206], [217, 103, 241], [101, 148, 14], [238, 104, 60]]
# COLOURS = blue, green, orange
COLOURS = [[19, 146, 206], [101, 148, 14], [238, 104, 60]]
COLOURS = [
    [(rgb_value / 128 - 1) for rgb_value in rgb_triplet] for rgb_triplet in COLOURS
]


def get_monitor_and_dir(testing: bool):
    if testing:
        # laptop
        monitor = {
            "resolution": (1920, 1080),  # in pixels
            "Hz": 60,  # screen refresh rate in Hz
            "width": 33,  # in cm
            "distance": 50,  # in cm
        }

        directory = r"../../Testing/"

    else:
        # lab
        monitor = {
            "resolution": (1920, 1080),  # in pixels
            "Hz": 239,  # screen refresh rate in Hz
            "width": 53,  # in cm
            "distance": 70,  # in cm
        }

        directory = r"C:\Users\Anna_vidi\Desktop\data"

    return monitor, directory


def get_settings(monitor: dict, directory, colour_assignment):
    window = visual.Window(
        color=("#7F7F7F"),
        size=monitor["resolution"],
        units="pix",
        fullscr=True,
    )

    degrees_per_pixel = degrees(atan2(0.5 * monitor["width"], monitor["distance"])) / (
        0.5 * monitor["resolution"][0]
    )

    colour_3 = {"red": COLOURS[2], "blue": COLOURS[0], "green": COLOURS[1]}[
        colour_assignment
    ]
    COLOURS.remove(colour_3)
    [colour_1, colour_2] = random.sample(COLOURS, 2)

    return dict(
        deg2pix=lambda deg: round(deg / degrees_per_pixel),
        # move the dial a quarter circle per second
        dial_step_size=(0.5 * pi) / monitor["Hz"],
        window=window,
        keyboard=Keyboard(),
        mouse=visual.CustomMouse(win=window, visible=False),
        monitor=monitor,
        directory=directory,
        colours=[colour_1, colour_2, colour_3],
    )
