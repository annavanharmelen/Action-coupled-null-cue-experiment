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
    options = ["orange", "green", "blue"]
    if existing_participants.colour_assignment.tolist()[-1] != "0":
        colour_index = (
            options.index(existing_participants.colour_assignment.tolist()[-1]) + 1
        )
        if colour_index == 3:
            colour_index = 0
        colour_assignment = options[colour_index]
    else:
        colour_assignment = options[0]

    # Add newly made participant
    new_participant = pd.DataFrame(
        {
            "age": [age],
            "participant_number": [participant],
            "session_number": [session],
            "colour_assignment": [colour_assignment],
        }
    )
    all_participants = pd.concat(
        [existing_participants, new_participant], ignore_index=True
    )

    return all_participants, colour_assignment
