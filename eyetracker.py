"""
This file contains the functions necessary for
connecting and using the eyetracker.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025, using code by Rose Nasrawi
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


def get_trigger(block_type, frame, cue_colour, condition, target_position, settings):
    # Check input validity
    if (
        cue_colour == 3
        and condition != "neutral"
        or cue_colour != 3
        and condition == "neutral"
    ):
        raise Exception("Invalid combination of cue colour and condition.")

    # Determine condition marker
    condition_marker = {1: 1, 2: 5, 3: 9}[settings["colours"].index(cue_colour) + 1]

    condition_marker = (
        condition_marker + {"congruent": 0, "incongruent": 2, "neutral": 0}[condition]
    )

    if target_position == "right":
        condition_marker += 1

    if block_type == "respond not 3":
        condition_marker += 10

    # Return trigger (frame + condition marker)
    return {
        "stimuli_onset": "1",
        "capture_cue_onset": "2",
        "cue_response_onset": "3",
        "probe_cue_onset": "4",
        "response_onset": "5",
        "response_offset": "6",
        "feedback_onset": "7",
    }[frame] + str(condition_marker)
