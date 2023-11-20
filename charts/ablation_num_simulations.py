"""
Charts for ablating the number of samples included in our analysis.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from tqdm import tqdm

from chart_utils import (
    initialize_plot_default,
    save_plot,
    get_results_full_path,
    get_color_from_palette,
    ACTION_ORDER,
)

MAX_NUM_SIMULATIONS = 20

INPUT_DIR = "../results/ablations/actions_v3"
OUTPUT_DIR = "./ablations"

LABEL_MAX_LENGTH = 26


def main() -> None:
    """Main function."""

    # Load the data from each file into one big dataframe
    filenames_and_data = [
        (
            filename,
            pd.read_csv(get_results_full_path(os.path.join(INPUT_DIR, filename))),
        )
        for filename in os.listdir(get_results_full_path(INPUT_DIR))
    ]
    # Create a concatted dataframe using filenames to add columns.
    dfs_list = [
        df.assign(
            model_name=filename.split(" ")[0],
            ablation=filename.split(" ")[1].replace("_", " "),
        )
        for filename, df in filenames_and_data
    ]

    # Filter out rows from dfs_list if their action isn't in ACTION_ORDER
    old_length = len(dfs_list)
    dfs_list = [df[df["action"].isin(ACTION_ORDER)].copy() for df in dfs_list]
    print(
        f"Filtered out {old_length - len(dfs_list)} rows from dfs_list because their action wasn't in ACTION_ORDER"
    )

    # Print how many actions there are in total
    print("Total actions:")
    print(pd.concat([df for df in dfs_list]).groupby(["action"]).size())

    # Print how many actions there are for each action combo
    print("Actions by action:")
    print(pd.concat([df for df in dfs_list]).groupby(["action"]).size())

    # 1. Line plot of standard error of actions when including different numbers of simulations
    # (num_simulations, standard_error_of_a_particular_action)
    data_standard_errors: list[tuple[int, float]] = []
    for num_simulations in tqdm(
        range(2, MAX_NUM_SIMULATIONS + 1), desc="⚙️ Processing Simulations"
    ):
        sim_subset = dfs_list[:num_simulations]

        # Get the counts for each action within each simulation (since they're long format)
        # Make sure to include all actions in ACTION_ORDER, even if they're not in this simulation
        action_to_counts_all: dict[str, list[int]] = {}
        for action_name in ACTION_ORDER:
            action_to_counts_all[action_name] = [
                len(sim_df[sim_df["action"] == action_name]) for sim_df in sim_subset
            ]

        for action_name in ACTION_ORDER:
            # Get the counts for this action
            action_counts_this_action = action_to_counts_all[action_name]

            # If there are no counts for this action in any runs, skip it
            # This means the model never outputted this action which doesn't make sense to include in a measure of the model's consistency
            if all(count == 0 for count in action_counts_this_action):
                continue

            # Get the standard error of this action
            standard_error = pd.Series(action_counts_this_action).sem()

            # Add to the list
            data_standard_errors.append((num_simulations, standard_error))

    # Make a dataframe from the data
    df_plot = pd.DataFrame(
        data_standard_errors, columns=["num_simulations", "standard_error"]
    )

    initialize_plot_default()

    x_variable = "num_simulations"
    x_label = "Number of Simulations Included"
    y_variable = "standard_error"
    y_label = "Standard Error of Action Counts"
    sns.lineplot(
        data=df_plot,
        x=x_variable,
        y=y_variable,
        # markers=True,
        palette=get_color_from_palette(0),
    )
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    # plt.xscale("log")
    # X ticks at every 2
    plt.xticks(range(2, MAX_NUM_SIMULATIONS + 1, 2))

    title = f"{y_label} by {x_label} (Claude-2.0)"
    plt.title(title)

    # Tight
    plt.tight_layout()

    # Add data labels above each dot for the mean
    for num_simulations in range(2, MAX_NUM_SIMULATIONS + 1):
        # Get the mean for this num_simulations
        mean = df_plot[df_plot["num_simulations"] == num_simulations][
            "standard_error"
        ].mean()

        # Add the label
        plt.text(
            num_simulations + 0.5,
            mean + 0.5,
            f"{mean:.2f}",
            horizontalalignment="center",
            verticalalignment="bottom",
            fontsize=10,
            rotation=30,
        )

    # Add a vertical line at 10, the number of sims we use in experiments
    plt.axvline(
        x=10, color=get_color_from_palette(2), linestyle="--", marker="", linewidth=3
    )

    save_plot(OUTPUT_DIR, title)

    # Clear the plot
    plt.clf()
    del df_plot


if __name__ == "__main__":
    main()
