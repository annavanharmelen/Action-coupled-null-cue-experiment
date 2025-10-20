"""
This file contains the functions necessary for
connecting and using the eyetracker.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025, using code by Ezra Nasrawi
"""

from lib import eyelinker
from psychopy import event
import os


class Eyelinker:
    """
    usage:

       from eyetracker import Eyelinker

    To initialise:

       eyelinker = Eyelinker(participant, session, window, directory)
       eyelinker.calibrate()
    """

    def __init__(self, participant, session, window, directory) -> None:
        """
        This also connects to the tracker
        """
        self.directory = directory
        self.window = window
        self.tracker = eyelinker.EyeLinker(
            window=window, eye="RIGHT", filename=f"{session}_{participant}.edf"
        )
        self.tracker.init_tracker()

    def start(self):
        self.tracker.start_recording()

    def calibrate(self):
        self.tracker.calibrate()

    def stop(self):
        os.chdir(self.directory)

        self.tracker.stop_recording()
        self.tracker.transfer_edf()
        self.tracker.close_edf()

    def send_trigger(self, trigger):
        self.tracker.send_message(f"trig{trigger}")


def get_trigger(
    frame,
    block_type,
    congruency,
    target_colour,
    target_position,
    target_orientation,
):
    # Determine condition marker
    condition_marker = {
        "stimuli_onset": 1,
        "capture_cue_onset": 51,
        "probe_cue_onset": 101,
        "response_onset": 151,
        "response_offset": 201,
    }[frame]

    if block_type == "respond not 3":
        condition_marker += 24

    condition_marker = (
        condition_marker + {"congruent": 0, "incongruent": 8, "neutral": 16}[congruency]
    )

    if target_colour == 2:
        condition_marker += 4

    if target_position == "right":
        condition_marker += 2

    if target_orientation == "anticlockwise":
        condition_marker += 1

    if (condition_marker + 1) % 50 == 0 or condition_marker > 250:
        info = f"Created condition marker ({condition_marker}) doesn't exist. Received:  {frame}, {block_type}, {congruency}, {target_colour}, {target_position}, {target_orientation}"
        raise Exception(info)

    # Return trigger
    return condition_marker
