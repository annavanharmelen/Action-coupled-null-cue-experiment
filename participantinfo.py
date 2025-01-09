"""
This file contains the functions necessary for
collecting participant data.
To run the 'action coupled null-cue' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

import random
import pandas as pd


def get_participant_details(existing_participants: pd.DataFrame, testing):
    # Generate random & unique participant number
    participant = random.randint(10, 99)
    while participant in existing_participants.participant_number.tolist():
        participant = random.randint(10, 99)

    print(f"Participant number: {participant}")

    if not testing:
        # Get participant age
        age = int(input("Participant age: "))
    else:
        age = 00

    # Insert session number
    session = max(existing_participants.session_number) + 1

    # Determine colour assignment
    total_options = 8 * ["red", "green", "blue"]

    for option in total_options:
        if option in existing_participants.colour_assignment.tolist():
            total_options.remove(option)

    random.shuffle(total_options)
    colour_assignment = total_options[0]

    # Add newly made participant
    new_participant = pd.DataFrame(
        {"age": [age], "participant_number": [participant], "session_number": [session], "colour_assignment": [colour_assignment]}
    )
    all_participants = pd.concat(
        [existing_participants, new_participant], ignore_index=True
    )

    return all_participants
