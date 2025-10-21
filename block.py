"""
This file contains the functions necessary for
creating and running a full block of trials start-to-finish.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

import random
from stimuli import show_text
from response import wait_for_key


def create_blocks(n_blocks):
    if n_blocks % 2 != 0:
        raise Exception("Expected number of blocks to be divisible by 2.")

    # Generate an equal number of blocks of all types
    # ensure also that before and after main break there are equal numbers of both block types
    block_types = ["respond 3", "respond not 3"]
    blocks_part_1 = (n_blocks // 4) * block_types
    blocks_part_2 = (n_blocks // 4) * block_types

    random.shuffle(blocks_part_1)
    random.shuffle(blocks_part_2)

    blocks = blocks_part_1 + blocks_part_2

    # Save list of sets of block numbers (in order) + block types
    blocks = list(zip(range(1, n_blocks + 1), blocks))

    return blocks


def create_block(n_trials):
    if n_trials % 24 != 0:
        raise Exception("Expected number of trials to be divisible by 24.")

    # Generate equal distribution of congruencies,
    congruencies = (
        n_trials // 3 * ["congruent"]
        + n_trials // 3 * ["incongruent"]
        + n_trials // 3 * ["neutral"]
    )

    # Generate equal distribution of target colours
    target_colours = n_trials // 8 * (n_trials // 6 * [1] + n_trials // 6 * [2])

    # Generate equal distribution of target positions
    target_locations = (
        n_trials // 4 * (n_trials // 12 * ["left"] + n_trials // 12 * ["right"])
    )

    # Generate equal distribution of target orientations
    target_orientations = n_trials // 2 * ["clockwise", "anticlockwise"]

    # Create trial parameters for all trials
    trials = list(
        zip(congruencies, target_colours, target_locations, target_orientations)
    )
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
        "Now is the time to take a longer break. You're still hooked up "
        "to the EEG system, but you can relax a bit."
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

def medium_break(current_block, n_blocks, hit, false_alarm, settings, eyetracker):
    blocks_left = n_blocks - current_block
    quartile =  current_block / n_blocks * 4 

    show_text(
        f"Hit: {hit}% \t False alarm: {false_alarm}%\n\n"
        f"Nice! You've finished {current_block} blocks already, "
        f"so you're {'three' if quartile == 3 else 'a'} quarter{'s' if quartile == 3 else ''} of the way through. "
        f"You have {blocks_left} block{'s' if blocks_left != 1 else ''} left. "
        "\n\nMake sure you take enough breaks, and remember you can ask the experimenter for something to drink."
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

def finish(n_blocks, settings):
    show_text(
        f"Congratulations! You successfully finished all {n_blocks} blocks!"
        "You're completely done now.\n\nPress SPACE to exit the experiment.",
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
