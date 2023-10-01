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
    """Simulate a military escalation."""

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_weeks",
        type=int,
        default=10,
        help="Number of turns (representing weeks) to simulate",
    )
    parser.add_argument(
        "--nation_model",
        type=str,
        default="gpt-3.5-turbo-0613",
        help="Agent model to use",
    )
    parser.add_argument(
        "--nations_config_filepath",
        type=str,
        default="data/nations_configs/nations_v1.csv",
    )
    parser.add_argument(
        "--action_config_filepath",
        type=str,
        default="data/action_configs/actions_v1.csv",
    )
    args = parser.parse_args()

    # Load nation configs
    with open(args.nations_config_filepath, "r", encoding="utf-8") as file:
        nations_config = pd.read_csv(file)

    # Load in the action config
    with open(args.action_config_filepath, "r", encoding="utf-8") as file:
        action_config = pd.read_csv(file)

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
    action_config = pd.DataFrame(data)

    # TODO Load action spec
    # with

    # Assume actions_spec is derived from your CSV data

    # Initialize things
    nations = [
        Nation(nation_config, args.nation_model) for nation_config in nations_config
    ]
    world = World(nations, action_config, max_weeks=args.max_weeks)

    # Main simulation loop
    while world.current_week < world.max_weeks:
        # 1. TODO Roll some random events
        # select random events fromt the random events yaml file
        # event_index = np.random.choice(
        #   len(events_data["events"])
        # )  # Assuming equal probabilities for simplicity
        # random_event = events_data["events"][event_index]

        # #once the random event is selected, it is added to the message history, with moves from both sides
        # queued_actions.append(Action(
        #     sender='moderator',
        #     recipient='all',
        #     content=random_event['prompt'],
        #     turn_index=turn_index,
        # ))

        # 2. Query the models
        queued_actions: list[Action] = []
        for nation in nations:
            queued_actions.append(nation.choose_actions(world))

        # Update state called here
        world.update_state(queued_actions)


if __name__ == "__main__":
    main()
