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
    show_text,
)
from eyetracker import get_trigger
import random


def generate_stimuli_characteristics(
    congruency, target_colour_id, target_location, target_orientation, settings
):
    distractor_colour_id = 2 if target_colour_id == 1 else 1

    if congruency == "congruent":
        target_colour = settings["colours"][target_colour_id - 1]
        distractor_colour = settings["colours"][distractor_colour_id - 1]
        cue_colour = target_colour
        cue_colour_id = target_colour_id
    elif congruency == "incongruent":
        target_colour = settings["colours"][target_colour_id - 1]
        distractor_colour = settings["colours"][distractor_colour_id - 1]
        cue_colour = distractor_colour
        cue_colour_id = distractor_colour_id
    elif congruency == "neutral":
        target_colour, distractor_colour = random.sample(settings["colours"][0:2], 2)
        cue_colour = settings["colours"][2]
        cue_colour_id = 3

    if target_orientation == "clockwise":
        target_orientation = random.randint(5, 85)
        distractor_orientation = random.randint(-5, -85)
    elif target_orientation == "anticlockwise":
        target_orientation = random.randint(-5, -85)
        distractor_orientation = random.randint(5, 85)

    if target_location == "left":
        stimuli_colours = [target_colour, distractor_colour]
        orientations = [target_orientation, distractor_orientation]
    else:
        stimuli_colours = [distractor_colour, target_colour]
        orientations = [distractor_orientation, target_orientation]

    return {
        "ITI": random.randint(500, 800) / 1000,
        "trial_condition": congruency,
        "stimuli_colours": stimuli_colours,
        "orientations": orientations,
        "left_orientation": orientations[0],
        "right_orientation": orientations[1],
        "capture_colour_id": cue_colour_id,
        "capture_colour": cue_colour,
        "target_colour": target_colour,
        "target_colour_id": target_colour_id,
        "target_bar": target_location,
        "target_orientation": target_orientation,
    }


def determine_response_required(block_type, congruency):
    if block_type == "respond 3" and congruency == "neutral":
        response_required = True
    elif block_type == "respond not 3" and congruency != "neutral":
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
    ITI,
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
    create_fixation_dot(settings, response_type)

    screens = [
        (0, lambda: 0 / 0, None),  # initial one to make life easier
        (ITI, lambda: create_fixation_dot(settings, response_type), None),
        (
            0.25,
            lambda: create_stimuli_frame(
                left_orientation,
                right_orientation,
                stimuli_colours,
                response_type,
                settings,
            ),
            "stimuli_onset",
        ),
        (0.75, lambda: create_fixation_dot(settings, response_type), None),
        (
            0.25,
            lambda: create_capture_cue_frame(capture_colour, response_type, settings),
            "capture_cue_onset",
        ),
        (1.25, lambda: create_fixation_dot(settings, response_type), None),
        (
            None,
            lambda: create_probe_cue_frame(target_colour, response_type, settings),
            None,
        ),
    ]

    # !!! The timing you pass to do_while_showing is the timing for the previously drawn screen. !!!

    for index, (duration, _, frame) in enumerate(screens[:-1]):
        # Send trigger if not testing
        if not testing and frame:
            eyetracker.send_trigger(
                get_trigger(
                    response_type,
                    frame,
                    capture_colour,
                    trial_condition,
                    target_bar,
                    settings,
                )
            )

        # Draw the next screen while showing the current one
        do_while_showing(duration, screens[index + 1][1], settings["window"])

    # The for loop only draws the probe cue, never shows it
    # So show it here
    if not testing:
        eyetracker.send_trigger(
            get_trigger(
                response_type,
                "probe_cue_onset",
                capture_colour,
                trial_condition,
                target_bar,
                settings,
            )
        )

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
        response_type,
        capture_colour,
    )

    if not testing:
        eyetracker.send_trigger(
            get_trigger(
                response_type,
                "response_offset",
                capture_colour,
                trial_condition,
                target_bar,
                settings,
            )
        )

    # Show performance
    create_fixation_dot(settings, response_type)
    show_text(
        f"{response['performance']}", settings["window"], (0, settings["deg2pix"](0.7))
    )

    if not testing:
        eyetracker.send_trigger(
            get_trigger(
                response_type,
                "feedback_onset",
                capture_colour,
                trial_condition,
                target_bar,
                settings,
            )
        )
    settings["window"].flip()
    sleep(0.25)

    return {
        "condition_code": get_trigger(
            response_type,
            "stimuli_onset",
            capture_colour,
            trial_condition,
            target_bar,
            settings,
        ),
        **response,
    }
