"""
Main simulation loop to run the military simulation.
"""

import argparse
import logging
from logging import Logger
import sys
import time

import pandas as pd
from tqdm import tqdm
import wandb

from nations import model_name_to_nation
from data_types import Action, NationResponse
from prompts import format_nation_descriptions_static, format_nation_states_dynamic
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
        default=14,
        help="Number of turns (representing days) to simulate",
    )
    parser.add_argument(
        "--nation_model",
        type=str,
        default="gpt-3.5-turbo-16k-0613",
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
        default="action_configs/actions_v4.csv",
    )
    parser.add_argument(
        "--project",
        dest="project",
        default="escalaition-v1",
        help="🏗️ Weights & Biases project name.",
    )
    parser.add_argument(
        "--disable_wandb",
        dest="disable_wandb",
        action="store_true",
        help="🚫Disable Weights & Biases logging.",
    )
    parser.add_argument(
        "--clamp_dynamic_variables",
        dest="clamp_dynamic_variables",
        action="store_true",
        default=False,
        help="🔒 Clamp dynamic variables to their min/max values.",
    )
    parser.add_argument(
        "--max_model_retries",
        dest="max_model_retries",
        type=int,
        default=5,
        help="⚠️ Max retries for querying a model.",
    )
    parser.add_argument(
        "--day_0_scenario",
        dest="day_0_scenario",
        type=str,
        default="",
        help="📝 Optional scenario to insert into the history for day 0.",
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
    world = World(logger, nations, action_config, max_days=args.max_days)

    # Initialize some run-wide trackers
    dynamic_column_names = nations[0].list_dynamic()
    dynamic_vars_whole_run = []
    model_response_text_column_names = [
        "day",
        "nation_name",
        "system_prompt",
        "user_prompt",
        "reasoning",
        "actions",
    ]
    model_response_text_whole_run = []
    model_response_costs_column_names = [
        "day",
        "nation_name",
        "completion_time_sec",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
    ]
    model_response_costs_whole_run = []
    actions_column_names = [
        "day",
        "self",
        "other",
        "action",
        "content",
    ]
    actions_whole_run = []

    # Log initial nation states (pre-update)
    dynamic_vars_today = [
        [0, nation.get_static("name")]
        + [nation.get_dynamic(column_name) for column_name in dynamic_column_names]
        for nation in nations
    ]
    dynamic_vars_whole_run.extend(dynamic_vars_today)

    # Main simulation loop
    logger.info(
        f"## 🎌 Starting simulation with the following nations: ##\n{format_nation_descriptions_static(world)}\n{format_nation_states_dynamic(world)}"
    )
    with tqdm(total=world.max_days, desc="Day", file=sys.stdout) as pbar:
        while world.current_day <= world.max_days:
            logger.info(f"📆 Beginning day {world.current_day} of {world.max_days}")

            # Store things for logging to wandb
            log_object = {
                "_progress/day": world.current_day,
                "_progress/percent_done": world.current_day / world.max_days * 100.0,
            }
            model_responses = []

            # Query the models
            queued_actions: list[Action] = []
            for nation_index, nation in enumerate(world.nations):
                response = None
                for _ in range(wandb.config.max_model_retries):
                    try:
                        response = nation.respond(world)
                        break
                    except Exception as exc:
                        logger.warning(
                            f"⚠️  Exception when querying {nation.get_static('name')}: {exc}"
                        )
                        time.sleep(1)
                if response is None:
                    logger.error(
                        f"🚨  Max retries exceeded for {nation.get_static('name')}, skipping"
                    )
                    continue
                action_print = utils.format_actions(response)
                nation_name = nation.get_static("name")
                logger.info(
                    f"⚙️  {nation_name} ({nation_index + 1}/{len(nations)}) on day {world.current_day}/{world.max_days} took {response.completion_time_sec}s, {response.prompt_tokens} prompt tokens, {response.completion_tokens} completion tokens:\nReasoning: {response.reasoning}\nActions: {action_print}"
                )
                queued_actions.extend(response.actions)
                model_responses.append(response)

            # Log formatted model responses
            response: NationResponse
            model_response_text_today = [
                [
                    world.current_day,
                    nation.get_static("name"),
                    response.system_prompt,
                    response.user_prompt,
                    response.reasoning,
                    utils.format_actions(response),
                ]
                for nation, response in zip(nations, model_responses)
            ]
            model_response_text_whole_run.extend(model_response_text_today)
            log_object["daily/model_responses_text"] = wandb.Table(
                columns=model_response_text_column_names,
                data=model_response_text_today,
            )
            model_response_costs_today = [
                [
                    world.current_day,
                    nation.get_static("name"),
                    response.completion_time_sec,
                    response.prompt_tokens,
                    response.completion_tokens,
                    response.total_tokens,
                ]
                for nation, response in zip(nations, model_responses)
            ]
            model_response_costs_whole_run.extend(model_response_costs_today)
            log_object["daily/model_responses_costs"] = wandb.Table(
                columns=model_response_costs_column_names,
                data=model_response_costs_today,
            )

            # Log token costs of responses this turn as a histogram
            log_object["costs/model_response_total_tokens_hist"] = wandb.Histogram(
                [response.total_tokens for response in model_responses]
            )
            log_object["costs/model_response_prompt_tokens_hist"] = wandb.Histogram(
                [response.prompt_tokens for response in model_responses]
            )
            log_object["costs/model_response_completion_tokens_hist"] = wandb.Histogram(
                [response.completion_tokens for response in model_responses]
            )
            log_object[
                "costs/model_response_completion_time_sec_hist"
            ] = wandb.Histogram(
                [response.completion_time_sec for response in model_responses]
            )

            # Log actions
            actions_today = [
                [
                    world.current_day,
                    action.self,
                    action.other,
                    action.name,
                    action.content,
                ]
                for action in queued_actions
            ]
            actions_whole_run.extend(actions_today)
            log_object["daily/actions"] = wandb.Table(
                columns=actions_column_names,
                data=actions_today,
            )

            # Update world state, advancing the day
            world.update_state(queued_actions)
            pbar.update(1)

            # Log current nation states (post-update)
            dynamic_vars_today = [
                [world.current_day, nation.get_static("name")]
                + [
                    nation.get_dynamic(column_name)
                    for column_name in dynamic_column_names
                ]
                for nation in nations
            ]
            dynamic_vars_whole_run.extend(dynamic_vars_today)
            log_object["daily/dynamic_vars"] = wandb.Table(
                columns=["day", "nation_name"] + dynamic_column_names,
                data=dynamic_vars_today,
            )

            # Create a metric for each dynamic variable for each nation
            for column_name in dynamic_column_names:
                for nation in nations:
                    nation_name = nation.get_static("name")
                    log_object[
                        f"dynamic_vars_split/{column_name}/{nation_name}"
                    ] = nation.get_dynamic(column_name)

            # Log the dynamic nation stats to console
            logger.info(
                f"📊 Day {world.current_day - 1} concluded. Current nation stats:\n{format_nation_states_dynamic(world)}"
            )

            wandb.log(log_object)

            utils.sleep_if_mock_wandb()

    # When done, log the full tables all together
    time.sleep(10)  # wait for wandb to catch up
    logging.info("📝 Logging full tables to wandb")
    log_object = {
        # "_progress/day": world.current_day,
        # "_progress/percent_done": 1.0,
    }
    log_object["whole_run/dynamic_vars"] = wandb.Table(
        columns=["day", "nation_name"] + dynamic_column_names,
        data=dynamic_vars_whole_run,
    )
    log_object["whole_run/actions"] = wandb.Table(
        columns=actions_column_names,
        data=actions_whole_run,
    )
    log_object["whole_run/model_responses_text"] = wandb.Table(
        columns=model_response_text_column_names,
        data=model_response_text_whole_run,
    )
    log_object["whole_run/model_responses_costs"] = wandb.Table(
        columns=model_response_costs_column_names,
        data=model_response_costs_whole_run,
    )
    wandb.log(log_object)
    time.sleep(5)

    wandb.finish()
    logger.info("🏁 Simulation complete!")
    time.sleep(5)


if __name__ == "__main__":
    main()
