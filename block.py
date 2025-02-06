"""
This file contains the functions necessary for
creating and running a full block of trials start-to-finish.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

import random
from trial import show_text
from response import wait_for_key


def create_blocks(n_blocks):
    if n_blocks % 2 != 0:
        raise Exception("Expected number of blocks to be divisible by 2.")

    # Generate an equal number of blocks of all types
    block_types = ["respond 3", "respond not 3"]
    blocks = (n_blocks // 2) * block_types

    random.shuffle(blocks)

    # Save list of sets of block numbers (in order) + block types
    blocks = list(zip(range(1, n_blocks + 1), blocks))

    return blocks


def create_block(n_trials):
    if n_trials % 12 != 0:
        raise Exception("Expected number of trials to be divisible by 12.")

    # Generate equal distribution of cue colours
    cue_colours = n_trials // 3 * [1] + n_trials // 3 * [2] + n_trials // 3 * [3]

    # Generate equal distribution of congruencies,
    congruencies = n_trials // 6 * (
        2 * ["congruent"] + 2 * ["incongruent"]
    ) + n_trials // 3 * ["neutral"]

    # Generate equal distribution of target locations
    target_locations = n_trials // 2 * ["left", "right"]

    # Create trial parameters for all trials
    trials = list(zip(cue_colours, congruencies, target_locations))
    random.shuffle(trials)

    return trials


def show_block_type(block_type, colour_assigned, settings, eyetracker):
    show_text(
        "Next: "
        f"respond when {'NOT ' if block_type == 'respond not 3' else ''}{colour_assigned}",
        settings["window"],
    )
    settings["window"].flip()

    if eyetracker:
        keys = wait_for_key(["space", "c"], settings["keyboard"])
        if "c" in keys:
            eyetracker.calibrate()
            eyetracker.start()
            return True
    else:
        wait_for_key(["space"], settings["keyboard"])

    return False


def block_break(current_block, n_blocks, hit, false_alarm, settings, eyetracker):
    blocks_left = n_blocks - current_block

    show_text(
        f"Hit: {hit}% \t False alarm: {false_alarm}%\n\n"
        f"You just finished block {current_block}, you {'only ' if blocks_left == 1 else ''}"
        f"have {blocks_left} block{'s' if blocks_left != 1 else ''} left. "
        "Take a break if you want to, but try not to move your head during this break."
        "\n\nPress SPACE when you're ready to continue.",
        settings["window"],
    )
    settings["window"].flip()

    if eyetracker:
        keys = wait_for_key(["space", "c"], settings["keyboard"])
        if "c" in keys:
            eyetracker.calibrate()
            eyetracker.start()
            return True
    else:
        wait_for_key(["space"], settings["keyboard"])

    return False


def long_break(n_blocks, hit, false_alarm, settings, eyetracker):
    show_text(
        f"Hit: {hit}% \t False alarm: {false_alarm}%\n\n"
        f"You're halfway through! You have {n_blocks // 2} blocks left. "
        "Now is the time to take a longer break. Maybe get up, stretch, walk around."
        "\n\nPress SPACE whenever you're ready to continue again.",
        settings["window"],
    )
    settings["window"].flip()

    if eyetracker:
        keys = wait_for_key(["space", "c"], settings["keyboard"])
        if "c" in keys:
            eyetracker.calibrate()
            return True
    else:
        wait_for_key(["space"], settings["keyboard"])

    return False


def finish(n_blocks, settings):
    show_text(
        f"Congratulations! You successfully finished all {n_blocks} blocks!"
        "You're completely done now. Press SPACE to exit the experiment.",
        settings["window"],
    )
    settings["window"].flip()

    wait_for_key(["space"], settings["keyboard"])


def quick_finish(settings):
    show_text(
        f"You've exited the experiment. Press SPACE to close this window.",
        settings["window"],
    )
    settings["window"].flip()

    wait_for_key(["space"], settings["keyboard"])
