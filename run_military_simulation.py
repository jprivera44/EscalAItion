"""
Main simulation loop to run the military simulation.
"""

import argparse
import logging
from logging import Logger
import sys

import pandas as pd
from tqdm import tqdm
import wandb

from nations import model_name_to_nation
from data_types import Action
import utils
from world import World


def main():
    """Simulate a military escalation."""

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", dest="seed", type=int, default=0, help="Random seed")
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
        default="nations_configs/nations_v1.csv",
    )
    parser.add_argument(
        "--action_config_filepath",
        type=str,
        default="action_configs/actions_v1.csv",
    )
    parser.add_argument(
        "--project",
        dest="project",
        default="escalaition",
        help="🏗️ Weights & Biases project name.",
    )
    parser.add_argument(
        "--disable_wandb",
        dest="disable_wandb",
        action="store_true",
        help="🚫Disable Weights & Biases logging.",
    )
    args = parser.parse_args()

    # Initialize weights and biases
    wandb.init(
        project=args.project,
        save_code=True,
        config=vars(args),
        mode="disabled" if args.disable_wandb else "online",
        settings=wandb.Settings(code_dir="."),
    )
    assert wandb.run is not None

    utils.set_seed(wandb.config.seed)

    # Load nation configs
    with open(args.nations_config_filepath, "r", encoding="utf-8") as file:
        nations_config = pd.read_csv(file)

    # Load in the action config
    with open(args.action_config_filepath, "r", encoding="utf-8") as file:
        action_config = pd.read_csv(file)

    # Initialize other things
    logger: Logger = logging.getLogger(__name__)
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    logger.info("Initializing Nations")
    nations = [
        model_name_to_nation(nation_config, model_name=args.nation_model)
        for _, nation_config in nations_config.iterrows()
    ]
    logger.info("Initializing World")
    world = World(nations, action_config, max_days=args.max_days)

    # Main simulation loop
    logger.info("Starting simulation")

    with tqdm(total=world.max_days, desc="Day", file=sys.stdout) as pbar:
        while world.current_day <= world.max_days:
            logger.info(f"📆 Beginning day {world.current_day} of {world.max_days}")
            # Query the models
            queued_actions: list[Action] = []
            for nation_index, nation in enumerate(world.nations):
                response = nation.respond(world)
                action_print = "\n\t".join(
                    [
                        f"{action.self} -> {action.other} : {action.name} {action.content}"
                        for action in response.actions
                    ]
                )
                nation_name = nation.get_static("name")
                logger.info(
                    f"⚙️  Response from {nation_name} ({nation_index + 1}/{len(nations)}) took {response.completion_time_sec}s, {response.prompt_tokens} prompt tokens, {response.completion_tokens} completion tokens:\nReasoning: {response.reasoning}\nActions: {action_print}"
                )
                queued_actions.extend(response.actions)

            # Update world state, advancing the day
            world.update_state(queued_actions)
            pbar.update(1)

    logger.info("🏁 Simulation complete!")


if __name__ == "__main__":
    main()
