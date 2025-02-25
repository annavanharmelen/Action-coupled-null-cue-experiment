"""
This file contains the functions necessary for
practising the trials and the use of the report dial.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from trial import (
    single_trial,
    generate_stimuli_characteristics,
    determine_response_required,
)
from stimuli import make_one_bar, create_fixation_dot, show_text
from response import get_response, wait_for_key
from block import show_block_type
from psychopy import event
from psychopy.hardware.keyboard import Keyboard
from time import sleep
import random
from numpy import mean

# 1. Practice response dial with a visible bar
# 2. Practice full trials - block type 1
# 3. Practice full trials - block type 2


def practice(testing, colour_assignment, settings):
    # Practice response dial
    practice_dial(testing, settings)

    # Decide which type of block to practice first
    block_types = ["respond 3", "respond not 3"]
    random.shuffle(block_types)

    # Practice separate block types (random order)
    practice_indefinitely(block_types[0], colour_assignment, True, settings)
    practice_indefinitely(block_types[1], colour_assignment, False, settings)


def practice_dial(testing, settings):
    # Show explanation
    show_text(
        f"Welcome to the practice trials. You will practice each part until you feel comfortable. \
            \nPress SPACE to start the practice session.",
        settings["window"],
    )
    settings["window"].flip()
    wait_for_key(["space"], settings["keyboard"])

    # Practice dial until user chooses to stop
    try:
        while True:
            target_bar = "left"
            target = generate_stimuli_characteristics(
                3, "neutral", target_bar, settings
            )
            target_orientation = target["target_orientation"]
            target_colour = None

            practice_bar = make_one_bar(
                target_orientation, "#eaeaea", "middle", settings
            )

            report: dict = get_response(
                target_orientation,
                target_colour,
                False,
                settings,
                testing,
                None,
                1,
                target_bar,
                None,
                None,
                [practice_bar],
            )

            create_fixation_dot(settings, "practice")
            show_text(
                f"{report['performance']}",
                settings["window"],
                (0, settings["deg2pix"](0.5)),
            )
            settings["window"].flip()
            sleep(0.5)

    except KeyboardInterrupt:
        show_text(
            "You decided to stop practising the response dial."
            "\nPress SPACE to start practicing full trials.",
            settings["window"],
        )
        settings["window"].flip()
        wait_for_key(["space"], settings["keyboard"])


def practice_indefinitely(block_type, colour_assignment, first_block, settings):
    try:
        # Create empty performance list
        hit = []
        false_alarm = []
        target_present = []

        # Show block type
        show_block_type(block_type, colour_assignment, settings, None)

        while True:
            cue_colour = random.choice([1, 2, 3])
            if cue_colour == 3:
                condition = "neutral"
            else:
                condition = random.choice(["congruent", "incongruent"])
            target_bar = random.choice(["left", "right"])

            stimulus = generate_stimuli_characteristics(
                cue_colour, condition, target_bar, settings
            )

            report: dict = single_trial(
                **stimulus,
                response_type=block_type,
                response_required=determine_response_required(block_type, cue_colour),
                settings=settings,
                testing=True,
            )

            hit.append(report["cue_hit"])
            false_alarm.append(report["cue_false_alarm"])
            target_present.append(determine_response_required(block_type, cue_colour))

    except KeyboardInterrupt:
        hit_score = round(mean(hit) / mean(target_present) * 100) if len(hit) > 1 else 0
        false_alarm_score = round(mean(false_alarm) / (1 - mean(target_present)) * 100) if len(false_alarm) > 1 else 0

        if first_block:
            show_text(
                "You decided to stop practising the first block type."
                f"\nDuring this practice, your score was:\n"
                f"Hit: {hit_score}% \t False alarm: {false_alarm_score}%\n"
                "\n\nPress SPACE to start practicing the other block type. ",
                settings["window"],
            )
            settings["window"].flip()
            wait_for_key(["space"], settings["keyboard"])

        else:
            show_text(
                "You decided to stop practicing the second block type."
                f"\nDuring this practice, your score was:\n"
                f"Hit: {hit_score}% \t False alarm: {false_alarm_score}%\n"
                "\n\nPress SPACE to start the experiment.",
                settings["window"],
            )
            settings["window"].flip()
            wait_for_key(["space"], settings["keyboard"])
