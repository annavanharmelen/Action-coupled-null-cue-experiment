"""
This file contains the functions necessary for
creating and running a single trial start-to-finish,
including eyetracker triggers.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual
from psychopy.core import wait
from time import time, sleep
from response import get_response
from stimuli import (
    create_fixation_dot,
    create_capture_cue_frame,
    create_stimuli_frame,
    create_probe_cue_frame,
)
from eyetracker import get_trigger
import random


def generate_stimuli_characteristics(cue_colour, condition, target_bar, settings):
    if condition == "congruent":
        target_colour = settings["colours"][cue_colour - 1]
        distractor_colour = settings["colours"][(2 if cue_colour == 1 else 1) - 1]
    elif condition == "incongruent":
        distractor_colour = settings["colours"][cue_colour - 1]
        target_colour = settings["colours"][(2 if cue_colour == 1 else 1) - 1]
    elif condition == "neutral":
        target_colour, distractor_colour = random.sample(settings["colours"][0:2], 2)

    orientations = [
        random.choice([-1, 1]) * random.randint(5, 85),
        random.choice([-1, 1]) * random.randint(5, 85),
    ]

    if target_bar == "left":
        target_orientation = orientations[0]
        stimuli_colours = [target_colour, distractor_colour]
    else:
        target_orientation = orientations[1]
        stimuli_colours = [distractor_colour, target_colour]

    return {
        "stimuli_colours": stimuli_colours,
        "capture_colour": settings["colours"][cue_colour - 1],
        "capture_colour_id": cue_colour,
        "trial_condition": condition,
        "left_orientation": orientations[0],
        "right_orientation": orientations[1],
        "target_bar": target_bar,
        "target_colour": target_colour,
        "target_orientation": target_orientation,
    }


def determine_response_required(block_type, cue_colour):
    if block_type == "respond 3" and cue_colour == 3:
        response_required = True
    elif block_type == "respond not 3" and cue_colour != 3:
        response_required = True
    else:
        response_required = False

    return response_required


def do_while_showing(waiting_time, something_to_do, window):
    """
    Show whatever is drawn to the screen for exactly `waiting_time` period,
    while doing `something_to_do` in the mean time.
    """
    window.flip()
    start = time()
    something_to_do()
    wait(waiting_time - (time() - start))


def single_trial(
    left_orientation,
    right_orientation,
    target_bar,
    target_colour,
    target_orientation,
    stimuli_colours,
    capture_colour,
    capture_colour_id,
    trial_condition,
    response_type,
    response_required,
    settings,
    testing,
    eyetracker=None,
):
    # Initial fixation cross to eliminate jitter caused by for loop
    create_fixation_dot(settings)

    screens = [
        (0, lambda: 0 / 0, None),  # initial one to make life easier
        (0.5, lambda: create_fixation_dot(settings), None),
        (
            0.25,
            lambda: create_stimuli_frame(
                left_orientation, right_orientation, stimuli_colours, settings
            ),
            "stimuli_onset",
        ),
        (0.75, lambda: create_fixation_dot(settings), None),
        (
            0.25,
            lambda: create_capture_cue_frame(capture_colour, settings),
            "capture_cue_onset",
        ),
        (1.25, lambda: create_fixation_dot(settings), None),
        (None, lambda: create_probe_cue_frame(target_colour, settings), None),
    ]

    # !!! The timing you pass to do_while_showing is the timing for the previously drawn screen. !!!

    for index, (duration, _, frame) in enumerate(screens[:-1]):
        # Send trigger if not testing
        if not testing and frame:
            trigger = get_trigger(frame, trial_condition, target_bar)
            eyetracker.tracker.send_message(f"trig{trigger}")

        # Draw the next screen while showing the current one
        do_while_showing(duration, screens[index + 1][1], settings["window"])

    # The for loop only draws the probe cue, never shows it
    # So show it here
    if not testing:
        trigger = get_trigger("probe_cue_onset", trial_condition, target_bar)
        eyetracker.tracker.send_message(f"trig{trigger}")

    settings["window"].flip()

    response = get_response(
        target_orientation,
        target_colour,
        response_required,
        settings,
        testing,
        eyetracker,
        trial_condition,
        target_bar,
    )

    if not testing:
        trigger = get_trigger("response_offset", trial_condition, target_bar)
        eyetracker.tracker.send_message(f"trig{trigger}")

    # Show performance
    create_fixation_dot(settings)
    show_text(
        f"{response['performance']}", settings["window"], (0, settings["deg2pix"](0.7))
    )

    if not testing:
        trigger = get_trigger("feedback_onset", trial_condition, target_bar)
        eyetracker.tracker.send_message(f"trig{trigger}")
    settings["window"].flip()
    sleep(0.25)

    return {
        "condition_code": get_trigger(
            response_type,
            "stimuli_onset",
            capture_colour_id,
            trial_condition,
            target_bar,
        ),
        **response,
    }


def show_text(input, window, pos=(0, 0), colour="#ffffff"):
    textstim = visual.TextStim(
        win=window, font="Courier New", text=input, color=colour, pos=pos, height=22
    )

    textstim.draw()
