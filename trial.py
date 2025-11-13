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
    draw_fixation_dot,
    create_capture_cue_frame,
    create_stimuli_frame,
    create_probe_cue_frame,
    show_text,
)
from eyetracker import get_trigger
import random


def generate_stimuli_characteristics(
    congruency, target_colour_id, target_location, target_direction, settings
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

    if target_direction == "clockwise":
        target_orientation = random.randint(5, 85)
        distractor_orientation = random.randint(-85, -5)
    elif target_direction == "anticlockwise":
        target_orientation = random.randint(-85, -5)
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
        "target_direction": target_direction,
        "target_orientation": target_orientation,
        "distractor_orientation": distractor_orientation,
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
    orientations,
    target_bar,
    target_colour,
    target_colour_id,
    target_direction,
    target_orientation,
    distractor_orientation,
    stimuli_colours,
    capture_colour,
    capture_colour_id,
    trial_condition,
    block_type,
    response_required,
    stimuli,
    settings,
    testing,
    eyetracker=None,
    eeg=None,
):
    # Initial fixation cross to eliminate jitter caused by for loop
    draw_fixation_dot(stimuli["fixation_dot"], stimuli["block_info_signal"], block_type)

    screens = [
        (0, lambda: 0 / 0, None),  # initial one to make life easier
        (
            ITI,
            lambda: draw_fixation_dot(
                stimuli["fixation_dot"], stimuli["block_info_signal"], block_type
            ),
            None,
        ),
        (
            0.25,
            lambda: create_stimuli_frame(
                stimuli,
                left_orientation,
                right_orientation,
                stimuli_colours,
                block_type,
                settings,
            ),
            "stimuli_onset",
        ),
        (
            0.75,
            lambda: draw_fixation_dot(
                stimuli["fixation_dot"], stimuli["block_info_signal"], block_type
            ),
            None,
        ),
        (
            0.25,
            lambda: create_capture_cue_frame(stimuli, capture_colour, block_type),
            "capture_cue_onset",
        ),
        (
            1.25,
            lambda: draw_fixation_dot(
                stimuli["fixation_dot"], stimuli["block_info_signal"], block_type
            ),
            None,
        ),
        (
            None,
            lambda: create_probe_cue_frame(stimuli, target_colour, block_type),
            None,
        ),
    ]

    # !!! The timing you pass to do_while_showing is the timing for the previously drawn screen. !!!

    for index, (duration, _, frame) in enumerate(screens[:-1]):
        # Send trigger if not testing
        if not testing and frame:
            trigger = get_trigger(
                frame,
                block_type,
                trial_condition,
                target_colour_id,
                target_bar,
                target_direction,
            )
            eeg.send_trigger(trigger)
            eyetracker.send_trigger(trigger)

        # Draw the next screen while showing the current one
        do_while_showing(duration, screens[index + 1][1], settings["window"])

    # The for loop only draws the probe cue, never shows it
    # So show it here
    if not testing:
        trigger = get_trigger(
            "probe_cue_onset",
            block_type,
            trial_condition,
            target_colour_id,
            target_bar,
            target_direction,
        )
        eeg.send_trigger(trigger)
        eyetracker.send_trigger(trigger)

    settings["window"].flip()

    response = get_response(
        stimuli,
        target_orientation,
        target_direction,
        target_colour,
        target_colour_id,
        response_required,
        settings,
        testing,
        eyetracker,
        eeg,
        trial_condition,
        target_bar,
        block_type,
        capture_colour,
    )

    if not testing:
        trigger = get_trigger(
            "response_offset",
            block_type,
            trial_condition,
            target_colour_id,
            target_bar,
            target_direction,
        )
        eeg.send_trigger(trigger)
        eyetracker.send_trigger(trigger)

    # Show performance
    draw_fixation_dot(stimuli["fixation_dot"], stimuli["block_info_signal"], block_type)
    show_text(
        f"{response['performance']}", settings["window"], (0, settings["deg2pix"](0.7))
    )
    settings["window"].flip()
    sleep(0.25)

    return {
        "condition_code": get_trigger(
            "stimuli_onset",
            block_type,
            trial_condition,
            target_colour_id,
            target_bar,
            target_direction,
        ),
        **response,
    }
