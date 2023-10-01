"""
Main simulation loop to run the military simulation.
"""

import argparse
import pandas as pd
from nations import Nation
from data_types import Action
from world import World


def main():
    """Simulate a military escalation."""

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_days",
        type=int,
        default=10,
        help="Number of turns (representing days) to simulate",
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

    # Initialize things
    nations = [
        Nation(nation_config, args.nation_model) for nation_config in nations_config
    ]
    world = World(nations, action_config, max_days=args.max_days)

    # Main simulation loop
    while world.current_day < world.max_days:
        # 2. Query the models
        queued_actions: list[Action] = []
        for nation in nations:
            nation_response = nation.respond(world)
            print(nation_response)
            queued_actions.extend(nation_response.actions)

        # Update state called here
        world.update_state(queued_actions)


if __name__ == "__main__":
    main()
