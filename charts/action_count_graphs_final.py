"""
Charts for action history.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from chart_utils import (
    ALL_MODEL_NAMES,
    ALL_SCENARIOS,
    SCENARIOS_TO_COLORS,
    MODELS_TO_COLORS,
    CAPSIZE_DEFAULT,
    ACTION_ORDER,
    ACTIONS_TO_SEVERITIES,
    SEVERITIES_ORDER,
    SEVERITY_TO_MARKER,
    SEVERITIES_TO_COLORS,
    initialize_plot_default,
    initialize_plot_bar,
    save_plot,
    get_results_full_path,
    get_color_from_palette,
)

INPUT_DIR = "../results/actions_v3"
OUTPUT_DIR_SEVERITY_BY_NATION = "./severity_by_nation"
OUTPUT_DIR_ACTIONS_OVER_TIME = "./actions_over_time"
OUTPUT_DIR_SEVERITY_BY_MODEL = "./severity_by_model"
OUTPUT_DIR_ACTIONS_BY_MODEL = "./actions_by_model"

PLOT_NUMBER_TO_CREATE = 2


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
    # Create a concatted dataframe using filenames to add columns. Split filenames on spaces, then first element is model_name and second is scenario
    dfs_list = [
        df.assign(
            model_name=filename.split(" ")[0],
            scenario=filename.split(" ")[1]
            .replace("MoreDrones", "3 Drones")
            .replace("A4", "Drone")
            .replace("_", " ")
            .replace("CyberAttack", "Cyberattack"),
        )
        for filename, df in filenames_and_data
    ]
    # df_all = pd.concat(dfs_list)

    # Filter out rows from dfs_list if their action isn't in ACTION_ORDER
    dfs_list = [df[df["action"].isin(ACTION_ORDER)].copy() for df in dfs_list]

    # Add a column for the severity of each action
    for df in dfs_list:
        df["severity"] = df["action"].map(ACTIONS_TO_SEVERITIES)
        # Make categorical so that the order is preserved in the graphs
        df["severity"] = pd.Categorical(
            df["severity"], categories=SEVERITIES_ORDER, ordered=True
        )

    # Print how many runs there are for each model_name, scenario combo
    print("Runs per model_name, scenario combo:")
    print(
        pd.concat([df for df in dfs_list])
        .groupby(["model_name", "scenario"], observed=True)
        .size()
    )

    # Print how many runs there are for each model_name, severity combo
    print("\nRuns per model_name, severity combo:")
    print(
        pd.concat([df for df in dfs_list])
        .groupby(["model_name", "severity"], observed=True)
        .size()
    )

    # For each scenario, for each model name, print out the % of actions that are each severity
    for scenario in ALL_SCENARIOS:
        print(f"\n{scenario} Scenario:")
        df_scenario = pd.concat(
            [df for df in dfs_list if df["scenario"].unique()[0] == scenario]
        )
        for model_name in ALL_MODEL_NAMES:
            df_model = df_scenario[df_scenario["model_name"] == model_name]
            print(f"\n{model_name}:")
            print(
                (
                    df_model.groupby("severity", observed=True).size()
                    / len(df_model)
                    * 100.0
                ).apply(lambda x: round(x, 2))
            )

    # LateX table: For each scenario, for each model name, print out a latex table row for:
    # |scenario|model|%provoking+-std|%aggressive+-std|placehold for escalation score+-std|
    print("\nLateX table:")
    print("    \\begin{tabular}{|c|c|c|c|c|}")
    print("        \\hline")
    print(
        r"        \textbf{Scenario} & \textbf{Model} & \textbf{\% Provoking Actions} & \textbf{\% Aggressive Actions} & \textbf{Avg. Escalation Score} \\"
    )
    print("        \\hline")
    for scenario in ALL_SCENARIOS:
        df_list_scenario = [
            df for df in dfs_list if df["scenario"].unique()[0] == scenario
        ]
        provoking_means = []
        aggressive_means = []
        provoking_stds = []
        aggressive_stds = []
        for model_name in ALL_MODEL_NAMES:
            df_list_model = [
                df
                for df in df_list_scenario
                if df["model_name"].unique()[0] == model_name
            ]
            provoking_percents = [
                (
                    df.groupby("severity", observed=True).size()["Provoking"]
                    / len(df)
                    * 100.0
                )
                for df in df_list_model
            ]
            aggressive_percents = []
            for df in df_list_model:
                if "Aggressive" not in df.groupby("severity", observed=True).size():
                    aggressive_percents.append(0.0)
                else:
                    aggressive_percents.append(
                        (
                            df.groupby("severity", observed=True).size()["Aggressive"]
                            / len(df)
                            * 100.0
                        )
                    )
            provoking_means.append(np.mean(provoking_percents))
            aggressive_means.append(np.mean(aggressive_percents))
            provoking_stds.append(np.std(provoking_percents))
            aggressive_stds.append(np.std(aggressive_percents))

        for i, model_name in enumerate(ALL_MODEL_NAMES):
            # print(
            #     f"        {scenario} & {model_name} & {provoking_means:.2f} $\pm$ {np.std(provoking_percents):.2f} & {aggressive_means:.2f} $\pm$ {np.std(aggressive_percents):.2f} & TEMP $\pm$ TEMP \\\\"
            # )
            # Print the corresponding data, and bold the mean and std if the mean is the highest for that column
            provoking_mean = provoking_means[i]
            aggressive_mean = aggressive_means[i]
            provoking_std = provoking_stds[i]
            aggressive_std = aggressive_stds[i]
            provoking_mean_str = f"{provoking_mean:.2f}"
            aggressive_mean_str = f"{aggressive_mean:.2f}"
            provoking_std_str = f"{provoking_std:.2f}"
            aggressive_std_str = f"{aggressive_std:.2f}"
            if provoking_mean == max(provoking_means):
                provoking_mean_str = r"\textbf{" + provoking_mean_str + "}"
                provoking_std_str = r"\textbf{" + provoking_std_str + "}"
            if aggressive_mean == max(aggressive_means):
                aggressive_mean_str = r"\textbf{" + aggressive_mean_str + "}"
                aggressive_std_str = r"\textbf{" + aggressive_std_str + "}"

            print(
                f"        {scenario} & {model_name} & {provoking_mean_str}\% $\pm$ {provoking_std_str}\% & {aggressive_mean_str}\% $\pm$ {aggressive_std_str}\% & TEMP $\pm$ TEMP \\\\"
            )

        print("        \\hline")
    print("    \\end{tabular}")

    # Plot a bunch of different bar graphs for different combos of models
    for model_name in ALL_MODEL_NAMES:
        # Create a DF of the counts of each model/scenario/action combo in each file
        print("Counting actions...")
        graphing_data_actions = []
        for df in dfs_list:
            if df["model_name"].unique()[0] != model_name:
                continue
            for scenario in ALL_SCENARIOS:
                for action in ACTION_ORDER:
                    count = len(
                        df[(df["scenario"] == scenario) & (df["action"] == action)]
                    )
                    severity = ACTIONS_TO_SEVERITIES[action]
                    graphing_data_actions.append(
                        {
                            "model_name": model_name,
                            "scenario": scenario,
                            "action": action,
                            "severity": severity,
                            "count": count,
                        }
                    )
        df_actions = pd.DataFrame(graphing_data_actions)

        # Creae a similar DF but by severity rather than actions
        groups_by_severity = [
            df.groupby(
                ["day", "model_name", "scenario", "severity"], observed=True
            ).size()
            for df in dfs_list
            if df["model_name"].unique()[0] == model_name
        ]
        graphing_data_severities = []
        for series in groups_by_severity:
            for (day, series_model_name, scenario, severity), count in series.items():
                graphing_data_severities.append(
                    {
                        "day": day,
                        "model_name": series_model_name,
                        "scenario": scenario,
                        "severity": severity,
                        "count": count,
                    }
                )
        df_severities = pd.DataFrame(graphing_data_severities)

        if len(df_actions) == 0 or len(df_severities) == 0:
            assert (
                len(df_actions) == 0 and len(df_severities) == 0
            ), f"df_actions is of length {len(df_actions)} and df_severities is of length {len(df_severities)} (expecting both 0)"
            print(f"❗ WARNING: Skipping {model_name} because it has no data")
            continue

        if PLOT_NUMBER_TO_CREATE == 1:
            # 1. Multi-line plot of severities over time
            for scenario in ALL_SCENARIOS:
                if scenario == "All Scenarios":
                    df_plot = df_severities.copy()
                else:
                    df_plot = df_severities[
                        df_severities["scenario"] == scenario
                    ].copy()
                if len(df_plot) == 0:
                    print(
                        f"❗ WARNING: Skipping {model_name} - {scenario} because it has no data"
                    )
                    continue

                initialize_plot_default()
                # palette = sns.color_palette(palette="Spectral_r", n_colors=27)
                # sns.set_palette(palette)
                # plt.rcParams["figure.figsize"] = (12, 8)
                x_variable = "day"
                y_variable = "count"
                x_label = "Day"
                y_label = "Daily Action Count"
                grouping = "severity"
                # Plot df_grouped
                sns.lineplot(
                    data=df_plot,
                    x=x_variable,
                    y=y_variable,
                    hue=grouping,
                    style=grouping,
                    hue_order=SEVERITIES_ORDER,
                    markers=SEVERITY_TO_MARKER,  # ["X", ".", "^", "v"],
                    # markers=True,
                    palette=SEVERITIES_TO_COLORS,
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
                plt.ylabel(y_label)
                plt.yscale("log")
                # Y axis ticks in non-scientific notation
                plt.yticks(
                    [1, 3, 10, 30],
                    ["1", "3", "10", "30"],
                )
                scenario_label = scenario
                title = f"Actions by Severity Over Time in {scenario_label} Scenario ({model_name})"
                plt.title(title)

                # Tight
                plt.tight_layout()

                save_plot(OUTPUT_DIR_ACTIONS_OVER_TIME, title)

                # Clear the plot
                plt.clf()
                del df_plot

        if PLOT_NUMBER_TO_CREATE == 2:
            # 2. Bar plot showing names grouped by scenario and for each model
            initialize_plot_bar()
            plt.rcParams["figure.figsize"] = (15, 4)
            x_variable = "action"
            x_label = "Action"
            y_variable = "count"
            y_label = "Total Action Count per Simulation"
            grouping = "scenario"
            grouping_order = ALL_SCENARIOS
            # palette = [
            #     SEVERITIES_TO_COLORS[severity] for severity in df_actions["severity"]
            # ]
            # Plot df_grouped
            sns.barplot(
                data=df_actions,
                x=x_variable,
                y=y_variable,
                order=ACTION_ORDER,
                hue=grouping,
                # grouping_order=grouping_order,
                palette=SCENARIOS_TO_COLORS,
                # order=df_grouped.index.get_level_values(x_variable).unique(),
                hue_order=grouping_order,
                capsize=CAPSIZE_DEFAULT,
                errorbar="ci",
            )
            plt.xlabel(x_label)
            # Ticks on the x axis
            plt.xticks(rotation=90)

            # Change x labels by automatically breaking long ones to 2 lines
            ax = plt.gca()
            labels = [item.get_text() for item in ax.get_xticklabels()]
            for label in labels:
                new_label = label
                if len(label) > LABEL_MAX_LENGTH:
                    # Break once after max length
                    remainder = label[LABEL_MAX_LENGTH:]
                    segments = remainder.split(" ", 1)
                    assert len(segments) == 2 or len(segments) == 1
                    new_label = label[:LABEL_MAX_LENGTH] + segments[0].strip()
                    if len(segments) == 2:
                        new_label += "\n" + segments[1]
                # Replace the label
                labels[labels.index(label)] = new_label

            ax.xaxis.tick_bottom()
            ax.xaxis.set_tick_params(width=1)
            ax.set_xticklabels(labels, ha="right")
            # Align labels better
            for idx, label in enumerate(ax.xaxis.get_ticklabels()):
                label.set_y(-0.05)
                label.set_x(idx)
                ax.text(
                    idx,
                    -0.1,
                    "|",
                    transform=ax.get_xaxis_transform(),
                    ha="center",
                    va="top",
                    color="k",
                )

            plt.ylabel(y_label)
            plt.yscale("log")
            # Y axis ticks in non-scientific notation
            plt.yticks(
                [0.03, 0.1, 0.3, 1, 3, 10, 30, 100],
                ["0.03", "0.1", "0.3", "1", "3", "10", "30", "100"],
            )

            title = f"{y_label} by Scenario ({model_name})"
            plt.title(title)
            plt.legend(title="Scenario", loc="best", framealpha=0.5)

            save_plot(OUTPUT_DIR_ACTIONS_BY_MODEL, title)

            # Clear the plot
            plt.clf()
            del df_actions

        if PLOT_NUMBER_TO_CREATE == 3:
            # 3. Counts of action severities by nation and scenario, 1 graph per model
            # Goal is to indicate how uniform the different nations are for each model.
            # Multibar where x axis is scenario and each of 3 groups has the 8 nations
            for scenario in ALL_SCENARIOS:
                groups_by_severity = [
                    df.groupby(["self", "scenario", "severity"], observed=True).size()
                    for df in dfs_list
                    if df["model_name"].unique()[0] == model_name
                    and df["scenario"].unique()[0] == scenario
                ]
                graphing_data_severities = []
                for series in groups_by_severity:
                    for (series_self, scenario, severity), count in series.items():
                        graphing_data_severities.append(
                            {
                                "self": series_self,
                                "scenario": scenario,
                                "severity": severity,
                                "count": count,
                            }
                        )
                df_plot = pd.DataFrame(graphing_data_severities)

                initialize_plot_bar()

                x_variable = "severity"
                x_label = "Severity of Action"
                y_variable = "count"
                y_label = "Total Action Count per Simulation"
                grouping = "self"
                grouping_label = "Nation"

                # Create a pallete mapping the nation color names to our normal palette colors
                palette = {
                    "Blue": get_color_from_palette(0),
                    "Green": get_color_from_palette(2),
                    "Orange": get_color_from_palette(1),
                    "Pink": get_color_from_palette(6),
                    "Purple": get_color_from_palette(4),
                    "Red": get_color_from_palette(3),
                    "White": get_color_from_palette(7),
                    "Yellow": get_color_from_palette(8),
                }

                sns.barplot(
                    data=df_plot,
                    x=x_variable,
                    y=y_variable,
                    order=SEVERITIES_ORDER,
                    hue=grouping,
                    # grouping_order=grouping_order,
                    # order=df_grouped.index.get_level_values(x_variable).unique(),
                    # hue_order=grouping_order,
                    capsize=CAPSIZE_DEFAULT,
                    errorbar="ci",
                    palette=palette,
                )
                plt.xlabel(x_label)
                # Ticks on the x axis
                plt.ylabel(y_label)
                plt.yscale("log")
                # Y axis labels in non-scientific notation
                plt.yticks(
                    [1, 3, 10, 30],
                    ["1", "3", "10", "30"],
                )

                title = f"Action Severity Counts by {grouping_label} in {scenario} Scenario ({model_name})"
                plt.title(title)
                legend_loc = "best"
                if model_name in ["GPT-3.5", "GPT-4-Base"]:
                    legend_loc = "lower left"
                plt.legend(
                    title=grouping_label,
                    loc=legend_loc,
                    # framealpha=0.5,
                    borderaxespad=0.0,
                    # bbox_to_anchor=(1.01, 1),
                    # loc="upper left",
                    handletextpad=0.1,
                    labelspacing=0.25,
                )

                save_plot(OUTPUT_DIR_SEVERITY_BY_NATION, title)
                plt.clf()
                del df_plot

    if PLOT_NUMBER_TO_CREATE == 4:
        # 4. Severities of Actions by Model (Different graph per scenario)
        # Regroup for df_actions, not filtering by model
        # Create a DF of the counts of each model/scenario/action combo in each file
        groups_by_action_all_models = [
            df.groupby(
                ["model_name", "scenario", "action", "severity"], observed=False
            ).size()
            for df in dfs_list
        ]
        graphing_data_actions_all_models = []
        for series in groups_by_action_all_models:
            for (
                # day,
                series_model_name,
                scenario,
                action,
                severity,
            ), count in series.items():
                graphing_data_actions_all_models.append(
                    {
                        # "day": day,
                        "model_name": series_model_name,
                        "scenario": scenario,
                        "action": action,
                        "severity": severity,
                        "count": count,
                    }
                )
        df_actions_all_models = pd.DataFrame(graphing_data_actions_all_models)
        for scenario in ALL_SCENARIOS:
            # Filter down to the rows of df_actions with this scenario
            df_plot = df_actions_all_models[
                df_actions_all_models["scenario"] == scenario
            ].copy()
            if len(df_plot) == 0:
                print(f"❗ WARNING: Skipping {scenario} because it has no data")
                continue

            initialize_plot_bar()
            x_variable = "severity"
            x_label = "Severity of Action"
            y_variable = "count"
            y_label = "Total Action Count per Simulation"
            grouping = "model_name"
            grouping_order = ALL_MODEL_NAMES
            # palette = [
            #     SEVERITIES_TO_COLORS[severity] for severity in df_actions["severity"]
            # ]
            # Plot df_grouped
            sns.barplot(
                data=df_plot,
                x=x_variable,
                y=y_variable,
                order=SEVERITIES_ORDER,
                hue=grouping,
                # grouping_order=grouping_order,
                # palette="bright",
                # order=df_grouped.index.get_level_values(x_variable).unique(),
                hue_order=grouping_order,
                capsize=CAPSIZE_DEFAULT,
                errorbar="ci",
                palette=MODELS_TO_COLORS,
            )
            plt.xlabel(x_label)
            # Ticks on the x axis
            plt.ylabel(y_label)
            plt.yscale("log")
            # Y axis labels in non-scientific notation
            plt.yticks(
                [0.1, 0.3, 1, 3, 10, 30],
                ["0.1", "0.3", "1", "3", "10", "30"],
            )

            title = f"Severity of Actions by Model ({scenario} Scenario)"
            plt.title(title)
            plt.legend(
                title="Model",
                loc="best",
                framealpha=0.5,
                borderaxespad=0.0,
                # bbox_to_anchor=(1.01, 1),
                # loc="upper left",
                handletextpad=0.1,
                labelspacing=0.25,
            )

            save_plot(OUTPUT_DIR_SEVERITY_BY_MODEL, title)

            # Clear the plot
            plt.clf()
            del df_plot


if __name__ == "__main__":
    main()
