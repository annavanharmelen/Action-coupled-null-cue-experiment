"""
This file contains the functions necessary for
creating the interactive response dial at the end of a trial.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import core, visual, event
from psychopy.hardware.keyboard import Keyboard
from math import cos, sin, degrees
from stimuli import create_fixation_dot, make_circle, RESPONSE_DIAL_SIZE
from time import time
from eyetracker import get_trigger


def turn_handle(pos, dial_step_size):
    x, y = pos
    pos = (
        x * cos(dial_step_size) + y * sin(dial_step_size),
        -x * sin(dial_step_size) + y * cos(dial_step_size),
    )

    # centre, distance, rad
    return pos


def get_report_orientation(key, turns, dial_step_size):
    report_orientation = degrees(turns * dial_step_size)

    if key == "z":
        report_orientation *= -1

    return report_orientation


def evaluate_cue_response(key_list, response_required):
    # Assume they pressed or didn't press incorrectly
    cue_response_hit = False
    cue_response_false_alarm = False

    # Check whether the opposite is true
    for i, key_press in enumerate(key_list[:-1]):
        time1 = round(key_press[1] * 1000, 2)
        time2 = round(key_list[i + 1][1] * 1000, 2)
        if (
            {key_press[0], key_list[i + 1][0]} == {"m", "z"}
            and time1 > -1500
            and time2 > -1500
        ):
            if response_required:
                cue_response_hit = True  # they should have pressed and did
            else:
                cue_response_false_alarm = True  # they shouldn't have pressed but did
            break

    return cue_response_hit, cue_response_false_alarm


def evaluate_response(report_orientation, target_orientation, key):
    report_orientation = round(report_orientation)

    signed_difference = target_orientation - report_orientation
    abs_difference = abs(target_orientation - report_orientation)

    if abs_difference > 90:
        abs_difference -= 180
        abs_difference *= -1

    performance = round(100 - abs_difference / 90 * 100)

    correct_key = (target_orientation > 0 and key == "m") or (
        target_orientation < 0 and key == "z"
    )

    return {
        "report_orientation": report_orientation,
        "performance": performance,
        "absolute_difference": abs_difference,
        "correct_key": correct_key,
        "signed_difference": signed_difference,
    }


def make_dial(settings, colour=None):
    dial_circle = make_circle(RESPONSE_DIAL_SIZE, settings, colour=colour)
    top_dial = make_circle(
        RESPONSE_DIAL_SIZE / 15,
        settings,
        pos=(0, RESPONSE_DIAL_SIZE),
        handle=True,
    )
    bottom_dial = make_circle(
        RESPONSE_DIAL_SIZE / 15,
        settings,
        pos=(0, -RESPONSE_DIAL_SIZE),
        handle=True,
    )

    return dial_circle, top_dial, bottom_dial


def get_response(
    target_orientation,
    target_colour,
    response_required,
    settings,
    testing,
    eyetracker,
    trial_condition,
    target_bar,
    block_type,
    capture_colour,
    additional_objects=[],
):
    keyboard: Keyboard = settings["keyboard"]
    window = settings["window"]

    # Check for pressed 'q'
    check_quit(keyboard)

    # These timing systems should start at the same time, this is almost true
    idle_reaction_time_start = time()
    keyboard.clock.reset()  # this reset ensures that premature key timings are relative to probe onset

    # Check if _any_ keys were prematurely pressed
    prematurely_pressed = [(p.name, p.rt) for p in keyboard.getKeys()]

    # Evaluate response to capture cue
    cue_response_hit, cue_response_false_alarm = evaluate_cue_response(
        prematurely_pressed, response_required
    )

    # Now clear keyboard before next response
    keyboard.clearEvents()

    turns = 0

    for item in additional_objects:
        item.draw()
        window.flip()

    # Wait indefinitely until the participant starts giving an answer
    keyboard.clearEvents()  # do it again to be sure
    pressed = event.waitKeys(keyList=["z", "m", "q"])

    response_started = time()
    idle_reaction_time = response_started - idle_reaction_time_start

    if "m" in pressed:
        key = "m"
        rad = settings["dial_step_size"]
    elif "z" in pressed:
        key = "z"
        rad = -settings["dial_step_size"]
    if "q" in pressed:
        raise KeyboardInterrupt()

    # Stop rotating the moment either of the following happens:
    # - the participant released the rotation key
    # - a second passed

    dial_circle, top_dial, bottom_dial = make_dial(settings, target_colour)

    if not testing and eyetracker:
        trigger = get_trigger(
            block_type,
            "response_onset",
            capture_colour,
            trial_condition,
            target_bar,
            settings,
        )
        eyetracker.tracker.send_message(f"trig{trigger}")

    while not keyboard.getKeys(keyList=[key]) and turns < settings["monitor"]["Hz"]:
        top_dial.pos = turn_handle(top_dial.pos, rad)
        bottom_dial.pos = turn_handle(bottom_dial.pos, rad)

        turns += 1

        for item in additional_objects:
            item.draw()

        dial_circle.draw()
        top_dial.draw()
        bottom_dial.draw()
        if not additional_objects:
            create_fixation_dot(settings, block_type)

        window.flip()

    response_time = time() - response_started

    return {
        "idle_reaction_time_in_ms": round(idle_reaction_time * 1000, 2),
        "response_time_in_ms": round(response_time * 1000, 2),
        "key_pressed": key,
        "turns_made": turns,
        "premature_pressed": True if prematurely_pressed else False,
        "premature_key": (
            [k[0] for k in prematurely_pressed] if prematurely_pressed else None
        ),
        "premature_timing": (
            [round(k[1] * 1000, 2) for k in prematurely_pressed]
            if prematurely_pressed
            else None
        ),
        "cue_hit": cue_response_hit,
        "cue_false_alarm": cue_response_false_alarm,
        **evaluate_response(
            get_report_orientation(key, turns, settings["dial_step_size"]),
            target_orientation,
            key,
        ),
    }


def wait_for_key(key_list, keyboard):
    keyboard: Keyboard = keyboard
    keyboard.clearEvents()
    keys = event.waitKeys(keyList=key_list)

    return keys


def check_quit(keyboard):
    if keyboard.getKeys("q"):
        raise KeyboardInterrupt()
