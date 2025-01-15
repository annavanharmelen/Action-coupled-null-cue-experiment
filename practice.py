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
    show_text,
)
from stimuli import make_one_bar, create_fixation_dot
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
        f"Welcome to the practice trials. You will practice each part until you press Q. \
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
                [practice_bar],
            )

            create_fixation_dot(settings)
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
            "\nPress SPACE to start practicing full trials."
            "\n\nRemember to press Q to stop practising these trials once you feel comfortable starting the real experiment.",
            settings["window"],
        )
        settings["window"].flip()
        wait_for_key(["space"], settings["keyboard"])


def practice_indefinitely(block_type, colour_assignment, first_block, settings):
    try:
        # Create empty performance list
        performance = []

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

            performance.append(report["cue_response"])

    except KeyboardInterrupt:
        if first_block:
            show_text(
                "You decided to stop practising the first block type. "
                f"\nDuring this practice, you correctly responded to the cue {round(mean(performance) * 100) if performance else 0}% of the time."
                "\n\nPress SPACE to start practicing the other block type. "
                "\n\nRemember to press Q to stop practising these trials once you feel comfortable starting the real experiment.",
                settings["window"],
            )
            settings["window"].flip()
            wait_for_key(["space"], settings["keyboard"])

        else:
            show_text(
                "You decided to stop practicing the second block type."
                f"\nDuring this practice, you correctly responded to the cue {round(mean(performance) * 100) if performance else 0}% of the time."
                f"\n\nPress SPACE to start the experiment.",
                settings["window"],
            )
            settings["window"].flip()
            wait_for_key(["space"], settings["keyboard"])
