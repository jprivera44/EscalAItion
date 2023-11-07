"""
Charts for action history.
"""

import os

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import seaborn as sns

from chart_utils import (
    CAPSIZE_DEFAULT,
    ACTION_ORDER,
    ACTIONS_TO_SEVERITIES,
    SEVERITIES_ORDER,
    initialize_plot_bar,
    save_plot,
    get_results_full_path,
)

MODEL_NAME = "GPT-3.5"
SCENARIO = "NEUTRAL"

INPUT_DIR = f"../results/prompt_ablations/{MODEL_NAME.lower()}/actions_v1"
OUTPUT_DIR = "./ablations"

PLOT_NUMBER_TO_CREATE = 1

LABEL_MAX_LENGTH = 26

ABLATION_PATTERNS_TO_PRETTY_NAMES = {
    "Neutral": "Unablated",
    "NoMessage": "No\nMessaging",
    "no_history": "No\nHistory",
    "NoPastActions": "No Past\nActions",
    "#shutdown": "Shutdown\nWhen Nuked",
    "no_goals": "No\nGoals",
    "#freedom": "Action\nAutonomy",
    "#simulation": "Low-Stakes\nSimulation",
}
ABLATION_NAME_ORDER = list(ABLATION_PATTERNS_TO_PRETTY_NAMES.values())


def filename_to_pretty_ablation_name(filename: str) -> str:
    """Format downloaded filenames into graphable names."""

    for pattern, pretty_name in ABLATION_PATTERNS_TO_PRETTY_NAMES.items():
        if pattern in filename:
            return pretty_name
    raise ValueError(f"Could not find a pretty name for filename {filename}")


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
    # Create a concatted dataframe using filenames to add columns. Split filenames on spaces, then first element is model_name and second is scenario
    dfs_list = [
        df.assign(
            ablation=filename_to_pretty_ablation_name(filename),
        )
        for filename, df in filenames_and_data
    ]

    # Filter out rows from dfs_list if their action isn't in ACTION_ORDER
    dfs_list = [df[df["action"].isin(ACTION_ORDER)].copy() for df in dfs_list]

    # Add a column for the severity of each action
    for df in dfs_list:
        df["severity"] = df["action"].map(ACTIONS_TO_SEVERITIES)
        # Make categorical so that the order is preserved in the graphs
        df["severity"] = pd.Categorical(
            df["severity"], categories=SEVERITIES_ORDER, ordered=True
        )

    # Print how many runs there are for each ablation
    print("Runs per ablation combo:")
    print(
        pd.concat([df for df in dfs_list]).groupby(["ablation"], observed=True).size()
    )

    # Print how many runs there are for each ablation, severity combo
    print("Runs per ablation, severity combo:")
    print(
        pd.concat([df for df in dfs_list])
        .groupby(["ablation", "severity"], observed=True)
        .size()
    )

    # # Create a DF of the counts of each model/scenario/action combo in each file
    # groups_by_action = [
    #     df.groupby(["ablation", "action", "severity"], observed=True).size()
    #     for df in dfs_list
    # ]
    # graphing_data_actions = []
    # for series in groups_by_action:
    #     for (
    #         # day,
    #         ablation,
    #         action,
    #         severity,
    #     ), count in series.items():
    #         graphing_data_actions.append(
    #             {
    #                 # "day": day,
    #                 "ablation": ablation,
    #                 "action": action,
    #                 "severity": severity,
    #                 "count": count,
    #             }
    #         )
    # df_severity_counts = pd.DataFrame(graphing_data_actions)
    # assert len(df_severity_counts) > 0

    # Create a DF of the ratio of each action severity per file
    groups_by_action = [
        df.groupby(["ablation", "action", "severity"], observed=True).size()
        for df in dfs_list
    ]
    graphing_data_actions = []
    for series in groups_by_action:
        # We need to calculate the number of each severity / total number of actions (rows) in that file
        total_actions = series.sum()
        for (
            # day,
            ablation,
            action,
            severity,
        ), count in series.items():
            graphing_data_actions.append(
                {
                    # "day": day,
                    "ablation": ablation,
                    "action": action,
                    "severity": severity,
                    "ratio": count / total_actions,
                }
            )
    df_severity_ratios = pd.DataFrame(graphing_data_actions)
    assert len(df_severity_ratios) > 0

    if PLOT_NUMBER_TO_CREATE == 1:
        # 1. Bar plot comparing the most severe action counts for each ablation
        df_plot = df_severity_ratios[
            df_severity_ratios["severity"] == "Aggressive"
        ].copy()
        assert len(df_plot) > 0

        initialize_plot_bar()
        # palette = sns.color_palette(palette="Spectral_r", n_colors=27)
        # sns.set_palette(palette)
        plt.rcParams["figure.figsize"] = (10, 8)
        x_variable = "ablation"
        x_label = "Prompt Ablation"
        y_variable = "ratio"
        y_label = "Ratio of Aggressive Actions"
        # grouping = "severity"
        # Plot df_grouped
        sns.barplot(
            data=df_plot,
            x=x_variable,
            y=y_variable,
            order=ABLATION_NAME_ORDER,
            capsize=CAPSIZE_DEFAULT,
            palette="colorblind",
            errorbar="ci"
            # hue_order=["Attack", "Defend", "Negotiate"],
        )
        # # Legend to the right of the plot
        # plt.legend(
        #     borderaxespad=0.0,
        #     bbox_to_anchor=(1.01, 1),
        #     loc="upper left",
        #     handletextpad=0.1,
        #     # labelspacing=1.5,
        # )
        plt.legend(loc="best", framealpha=0.5)  # title="Severity",
        plt.xlabel(x_label)
        # plt.xticks(rotation=30)
        plt.ylabel(y_label)
        # plt.yscale("log")
        # Y axis ticks in non-scientific notation
        # ticks = range(2e-3, 2e-2, 2e-3)
        # ticks = np.arange(0.002, 0.02, 0.002)
        # plt.yticks(
        #     ticks,
        #     [f"{tick:.2f}" for tick in ticks],
        # )
        # plt.yticks(
        #     [1, 3, 10, 30],
        #     ["1", "3", "10", "30"],
        # )
        scenario_label = SCENARIO.title()
        title = f"{y_label} over {x_label} in {scenario_label} Scenario ({MODEL_NAME})"
        plt.title(title)

        # Tight
        plt.tight_layout()

        save_plot(OUTPUT_DIR, title)

        # Clear the plot
        plt.clf()
        del df_plot


if __name__ == "__main__":
    main()
