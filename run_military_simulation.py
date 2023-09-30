"""
Main simulation loop to run the military simulation.
"""

from dataclasses import dataclass
import os
import sys
import time
import argparse
import yaml
import numpy as np
import random
import pandas as pd
from datetime import datetime
from collections import defaultdict

from nations import Nation
from data_types import Action
from world import World
from prompts import (
    get_agent_system_prompt,
    get_agent_user_prompt,
    get_moderator_system_prompt,
    get_model_user_prompt,
)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_weeks", type=int, default=10, help="Number of turns (weeks) to simulate"
    )
    parser.add_argument(
        "--agent_model",
        type=str,
        default="gpt-3.5-turbo-0613",
        help="Agent model to use",
    )
    parser.add_argument(
        "--world_model",
        type=str,
        default="gpt-3.5-turbo-0613",
    )
    parser.add_argument(
        "--agent_config_filepath",
        type=str,
        default="data/agent_configs/debug.csv",
    )
    args = parser.parse_args()

    # Load nation configs
    with open(args.nation_spec_filepath, "r") as file:
        all_nation_configs = pd.read_csv(file)

    # commenting this out for now
    # actions_spec = pd.read_csv('data/actions_spec.csv')

    # hard code in a pandas datafrae for the actions spec
    # Define the lists
    event_names = [
        "nuclear_launch_detected",
        "random_drone_strike",
        "power_outage",
        "cyber_attack",
        "negotiation",
    ]
    actions = ["Action1", "Action2", "Action3", "Action4", "Action5"]
    severities = ["Low", "Medium", "High"]

    # Define some hardcoded economic impact values
    economic_impact_values = np.random.uniform(
        -1.0, 1.0, 15
    )  # Generating 15 random values as an example

    # Mock action config for testing
    data = [
        {
            "event_name": "nuclear_launch_detected",
            "economic_impact": economic_impact_values[0],
            "action": "Action1",
            "severity": "High",
        },
        {
            "event_name": "random_drone_strike",
            "economic_impact": economic_impact_values[1],
            "action": "Action2",
            "severity": "Medium",
        },
        {
            "event_name": "power_outage",
            "economic_impact": economic_impact_values[2],
            "action": "Action3",
            "severity": "Low",
        },
        {
            "event_name": "cyber_attack",
            "economic_impact": economic_impact_values[3],
            "action": "Action4",
            "severity": "High",
        },
        {
            "event_name": "negotiation",
            "economic_impact": economic_impact_values[4],
            "action": "Action5",
            "severity": "Medium",
        },
    ]

    # Convert the list of dictionaries to a DataFrame
    action_configs = pd.DataFrame(data)

    # TODO Load action spec
    # with

    # Assume actions_spec is derived from your CSV data

    # Initialize things
    nations = [Nation(nation_config) for nation_config in all_nation_configs]
    world = World(nations, action_configs, max_weeks=args.max_weeks)

    # Main simulation loop
    while world.current_week < world.max_weeks:
        # 0. Increment the turn index
        world.current_week += 1

        # 1. Roll some random events
        # select random events fromt the random events yaml file
        event_index = np.random.choice(
            len(events_data["events"])
        )  # Assuming equal probabilities for simplicity
        random_event = events_data["events"][event_index]

        # #once the random event is selected, it is added to the message history, with moves from both sides
        # queued_actions.append(Action(
        #     sender='moderator',
        #     recipient='all',
        #     content=random_event['prompt'],
        #     turn_index=turn_index,
        # ))

        # 2. Query the models
        queued_actions: Action = []
        for model in models:
            response = model.query()

            queued_actions.append(
                Action(
                    sender=model.name,
                    recipient=model.recipient,
                    content=response.message,
                    timestamp=datetime.now(),
                )
            )

        # 3. Execute the queued actions by asking the moderator
        moderator_prompt = prompts.get_moderator_prompt(queued_actions, agents)
        moderator_response = moderator.query(moderator_prompt)


if __name__ == "__main__":
    main()
