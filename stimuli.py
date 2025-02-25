"""
This file contains the functions necessary for
creating the fixation cross and the bar stimuli.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual

ECCENTRICITY = 6
DOT_SIZE = 0.1  # radius of inner circle
TOTAL_DOT_SIZE = 0.35  # radius of outer circle
BAR_SIZE = [0.6, 4]  # width, height
RESPONSE_DIAL_SIZE = 2  # radius of circle

decentral_dot = fixation_dot = None


def create_fixation_dot(settings, block_type, colour="#eaeaea"):
    global decentral_dot, fixation_dot

    # Make fixation dot
    if decentral_dot is None:
        decentral_dot = visual.Circle(
            win=settings["window"],
            units="pix",
            radius=settings["deg2pix"](TOTAL_DOT_SIZE),
            pos=(0, 0),
            fillColor=colour,
        )
    decentral_dot.fillColor = colour

    if fixation_dot is None:
        fixation_dot = visual.Circle(
            win=settings["window"],
            units="pix",
            radius=settings["deg2pix"](DOT_SIZE),
            pos=(0, 0),
            fillColor="#000000",
        )

    decentral_dot.draw()
    fixation_dot.draw()

    create_block_info_signal(block_type, settings)


def show_text(input, window, pos=(0, 0), colour="#ffffff"):
    textstim = visual.TextStim(
        win=window, font="Courier New", text=input, color=colour, pos=pos, height=22
    )

    textstim.draw()


def make_one_bar(orientation, colour, position, settings):
    # Check input
    if position == "left":
        pos = (-settings["deg2pix"](ECCENTRICITY), 0)
    elif position == "right":
        pos = (settings["deg2pix"](ECCENTRICITY), 0)
    elif position == "middle":
        pos = (0, 0)
    else:
        raise Exception(f"Expected 'left' or 'right', but received {position!r}. :(")

    # Create bar stimulus
    bar_stimulus = visual.Rect(
        win=settings["window"],
        units="pix",
        width=settings["deg2pix"](BAR_SIZE[0]),
        height=settings["deg2pix"](BAR_SIZE[1]),
        pos=pos,
        ori=orientation,
        fillColor=colour,
    )

    return bar_stimulus


def make_circle(rad, settings, pos=(0, 0), handle=False, colour=None):
    circle = visual.Circle(
        win=settings["window"],
        radius=settings["deg2pix"](rad),
        edges=settings["deg2pix"](1),
        lineWidth=settings["deg2pix"](0.1),
        pos=(settings["deg2pix"](pos[0]), settings["deg2pix"](pos[1])),
    )

    if handle:
        circle.lineColor = "#eaeaea"
        circle.fillColor = settings["window"].color
    else:
        circle.lineColor = colour if colour else "#d4d4d4"
        circle.fillColor = None

    return circle


def create_stimuli_frame(
    left_orientation, right_orientation, colours, block_type, settings
):
    create_fixation_dot(settings, block_type)
    make_one_bar(left_orientation, colours[0], "left", settings).draw()
    make_one_bar(right_orientation, colours[1], "right", settings).draw()


def create_capture_cue_frame(colour, block_type, settings):
    create_fixation_dot(settings, block_type, colour)


def create_probe_cue_frame(colour, block_type, settings):
    create_fixation_dot(settings, block_type)
    make_circle(RESPONSE_DIAL_SIZE, settings, colour=colour).draw()


def create_block_info_signal(block_type, settings):
    if block_type == "respond 3":
        signal = "+"
    elif block_type == "respond not 3":
        signal = "-"
    else:
        signal = ""

    show_text(
        signal,
        settings["window"],
        pos=(settings["deg2pix"](7), -settings["deg2pix"](7)),
        colour="#999999",
    )
