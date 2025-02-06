"""
Main script for running the 'action coupled null-cue' experiment
made by Anna van Harmelen, 2025

see README.md for instructions if needed
"""

# Import necessary stuff
from psychopy import core
import pandas as pd
from participantinfo import get_participant_details
from set_up import get_monitor_and_dir, get_settings
from eyetracker import Eyelinker
from argparse import ArgumentParser
from trial import (
    determine_response_required,
    generate_stimuli_characteristics,
    single_trial,
)
from time import time
from numpy import mean
from practice import practice
import datetime as dt
from block import (
    create_blocks,
    create_block,
    show_block_type,
    block_break,
    long_break,
    finish,
    quick_finish,
)
import traceback

N_BLOCKS = 16
TRIALS_PER_BLOCK = 48


def main():
    """
    Data formats / storage:
     - eyetracking data saved in one .edf file per session
     - all trial data saved in one .csv per session
     - subject data in one .csv (for all sessions combined)
    """

    # Set whether this is a test run or not
    testing = False

    # Get monitor and directory information
    monitor, directory = get_monitor_and_dir(testing)

    # Get participant details and save in same file as before
    old_participants = pd.read_csv(
        rf"{directory}\participantinfo.csv",
        dtype={
            "participant_number": int,
            "session_number": int,
            "age": int,
            "trials_completed": str,
            "colour_assignment": str,
        },
    )
    new_participants, colour_assignment = get_participant_details(
        old_participants, testing
    )

    # Initialise set-up
    settings = get_settings(monitor, directory, colour_assignment)

    # Connect to eyetracker and calibrate it
    if not testing:
        eyelinker = Eyelinker(
            new_participants.participant_number.iloc[-1],
            new_participants.session_number.iloc[-1],
            settings["window"],
            settings["directory"],
        )
        eyelinker.calibrate()

    # Start recording eyetracker
    if not testing:
        eyelinker.start()
    
    # Practice until participant wants to stop
    practice(testing, colour_assignment, settings)

    # Initialise some stuff
    start_of_experiment = time()
    data = []
    current_trial = 0
    finished_early = True

    # Start experiment
    try:
        # Generate pseudo-random order of blocks
        blocks = create_blocks(2 if testing else N_BLOCKS)

        for block_nr, block_type in blocks:
            # Create temporary variable for saving block performance
            block_hit = []
            block_false_alarm = []
            block_target_present = []

            # Pseudo-randomly create conditions and target locations (so they're weighted)
            block_info = create_block(12 if testing else TRIALS_PER_BLOCK)

            # Remind participant of block type
            calibrated = True
            while calibrated:
                calibrated = show_block_type(
                    block_type,
                    colour_assignment,
                    settings,
                    eyetracker=None if testing else eyelinker,
                )

            # Clear keyboard cache before starting again
            settings["keyboard"].clearEvents()

            # Run trials per pseudo-randomly created info
            for cue_colour, condition, target_bar in block_info:
                current_trial += 1
                start_time = time()

                # Determine response trial or not
                response_required = determine_response_required(block_type, cue_colour)

                stimuli_characteristics: dict = generate_stimuli_characteristics(
                    cue_colour, condition, target_bar, settings
                )

                # Generate trial
                report: dict = single_trial(
                    **stimuli_characteristics,
                    response_type=block_type,
                    response_required=response_required,
                    settings=settings,
                    testing=testing,
                    eyetracker=None if testing else eyelinker,
                )
                end_time = time()

                # Save trial data
                data.append(
                    {
                        "trial_number": current_trial,
                        "block_type": block_type,
                        "block": block_nr,
                        "start_time": str(
                            dt.timedelta(seconds=(start_time - start_of_experiment))
                        ),
                        "end_time": str(
                            dt.timedelta(seconds=(end_time - start_of_experiment))
                        ),
                        **stimuli_characteristics,
                        **report,
                    }
                )
                block_hit.append(report["cue_hit"])
                block_false_alarm.append(report["cue_false_alarm"])
                block_target_present.append(response_required)

            # Calculate average performance score for most recent block
            hits = round(mean(block_hit) / mean(block_target_present) * 100)
            false_alarms = round(mean(block_false_alarm) / (1 - mean(block_target_present)) * 100)

            # Break after end of block, unless it's the last block.
            # Experimenter can re-calibrate the eyetracker by pressing 'c' here.
            calibrated = True
            if block_nr == N_BLOCKS // 2:
                while calibrated:
                    calibrated = long_break(
                        N_BLOCKS,
                        hits,
                        false_alarms,
                        settings,
                        eyetracker=None if testing else eyelinker,
                    )
                if not testing:
                    eyelinker.start()
            elif block_nr < N_BLOCKS:
                while calibrated:
                    calibrated = block_break(
                        block_nr,
                        N_BLOCKS,
                        hits,
                        false_alarms,
                        settings,
                        eyetracker=None if testing else eyelinker,
                    )

        finished_early = False

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        
    finally:
        # Stop eyetracker (this should also save the data)
        if not testing:
            eyelinker.stop()

        # Save all collected trial data to a new .csv
        pd.DataFrame(data).to_csv(
            rf"{settings['directory']}\data_session_{new_participants.session_number.iloc[-1]}{'_test' if testing else ''}.csv",
            index=False,
        )

        # Register how many trials this participant has completed
        new_participants.loc[new_participants.index[-1], "trials_completed"] = str(
            len(data)
        )

        # Save participant data to existing .csv file
        new_participants.to_csv(
            rf"{settings['directory']}\participantinfo.csv", index=False
        )

        # Done!
        if finished_early:
            quick_finish(settings)
        else:
            finish(N_BLOCKS, settings)

        core.quit()

    # Thanks for meedoen


if __name__ == "__main__":
    main()
