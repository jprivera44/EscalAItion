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
    ALL_MODEL_NAMES_WITH_GPT_4_BASE,
    ALL_SCENARIOS,
    SCENARIOS_TO_COLORS,
    MODELS_TO_COLORS,
    CAPSIZE_DEFAULT,
    ACTION_ORDER,
    ACTIONS_TO_SEVERITIES,
    LABELSIZE_DEFAULT,
    SEVERITIES_ORDER,
    SEVERITIES_ORDER_NEWLINES,
    SEVERITY_TO_MARKER,
    SEVERITIES_TO_COLORS,
    TIMELABEL_DEFAULT,
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
OUTPUT_DIR_DISTRIBUTIONS_ALL_ACTIONS = "./distributions_all_actions"

PLOT_NUMBER_TO_CREATE = 5  # -1 to create all plots

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
        for model_name in ALL_MODEL_NAMES_WITH_GPT_4_BASE:
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
    # |scenario|model|%Non-violent+-std|%Violent+-std|%Nuclear+-std|placehold for escalation score+-std|
    print("\nLateX table:")
    print("    \\begin{tabularx}{\\textwidth}{|c|c|X|X|X|X|}")
    print("        \\hline")
    print(
        r"        \textbf{Scenario} & \textbf{Model} & \textbf{\% Non-violent Escalation (Count)} & \textbf{\% Violent Escalation (Count)} & \textbf{\% Nuclear (Count)} & \textbf{Mean Escalation Score} \\"
    )
    print("        \\hline")
    gpt_4_base_rows = ""
    for scenario in ALL_SCENARIOS:
        df_list_scenario = [
            df for df in dfs_list if df["scenario"].unique()[0] == scenario
        ]
        nonviolent_means = []
        violent_means = []
        nuclear_means = []
        nonviolent_stds = []
        violent_stds = []
        nuclear_stds = []
        nonviolent_counts_mean = []
        violent_counts_mean = []
        nuclear_counts_mean = []
        for model_name in ALL_MODEL_NAMES_WITH_GPT_4_BASE:
            df_list_model = [
                df
                for df in df_list_scenario
                if df["model_name"].unique()[0] == model_name
            ]
            nonviolent_percents = []
            nonviolent_counts = []
            for df in df_list_model:
                if (
                    "Non-violent escalation"
                    not in df.groupby("severity", observed=True).size()
                ):
                    nonviolent_percents.append(0.0)
                    nonviolent_counts.append(0)
                else:
                    nonviolent_percents.append(
                        (
                            df.groupby("severity", observed=True).size()[
                                "Non-violent escalation"
                            ]
                            / len(df)
                            * 100.0
                        )
                    )
                    nonviolent_counts.append(
                        df.groupby("severity", observed=True).size()[
                            "Non-violent escalation"
                        ]
                    )

            violent_percents = []
            violent_counts = []
            for df in df_list_model:
                if (
                    "Violent escalation"
                    not in df.groupby("severity", observed=True).size()
                ):
                    violent_percents.append(0.0)
                    violent_counts.append(0)
                else:
                    violent_percents.append(
                        (
                            df.groupby("severity", observed=True).size()[
                                "Violent escalation"
                            ]
                            / len(df)
                            * 100.0
                        )
                    )
                    violent_counts.append(
                        df.groupby("severity", observed=True).size()[
                            "Violent escalation"
                        ]
                    )

            nuclear_percents = []
            nuclear_counts = []
            for df in df_list_model:
                if "Nuclear" not in df.groupby("severity", observed=True).size():
                    nuclear_percents.append(0.0)
                    nuclear_counts.append(0)
                else:
                    nuclear_percents.append(
                        (
                            df.groupby("severity", observed=True).size()["Nuclear"]
                            / len(df)
                            * 100.0
                        )
                    )
                    nuclear_counts.append(
                        df.groupby("severity", observed=True).size()["Nuclear"]
                    )
            nonviolent_means.append(np.mean(nonviolent_percents))
            nonviolent_stds.append(np.std(nonviolent_percents))
            nonviolent_counts_mean.append(np.mean(nonviolent_counts))
            violent_means.append(np.mean(violent_percents))
            violent_stds.append(np.std(violent_percents))
            violent_counts_mean.append(np.mean(violent_counts))
            nuclear_means.append(np.mean(nuclear_percents))
            nuclear_stds.append(np.std(nuclear_percents))
            nuclear_counts_mean.append(np.mean(nuclear_counts))

        for i, model_name in enumerate(ALL_MODEL_NAMES_WITH_GPT_4_BASE):
            # Print the corresponding data, and bold the mean and std if the mean is the highest for that column
            nonviolent_mean = nonviolent_means[i]
            violent_mean = violent_means[i]
            nuclear_mean = nuclear_means[i]
            nonviolent_std = nonviolent_stds[i]
            violent_std = violent_stds[i]
            nuclear_std = nuclear_stds[i]
            nonviolent_mean_str = f"{nonviolent_mean:.2f}"
            violent_mean_str = f"{violent_mean:.2f}"
            nuclear_mean_str = f"{nuclear_mean:.2f}"
            nonviolent_std_str = f"{nonviolent_std:.2f}"
            violent_std_str = f"{violent_std:.2f}"
            nuclear_std_str = f"{nuclear_std:.2f}"
            nonviolent_count_mean = nonviolent_counts_mean[i]
            violent_count_mean = violent_counts_mean[i]
            nuclear_count_mean = nuclear_counts_mean[i]
            nonviolent_count_mean_str = f"({nonviolent_count_mean:.2f})"
            violent_count_mean_str = f"({violent_count_mean:.2f})"
            nuclear_count_mean_str = f"({nuclear_count_mean:.2f})"
            if nonviolent_mean == max(nonviolent_means[:-1]):  # Skip GPT-4-Base
                nonviolent_mean_str = r"\textbf{" + nonviolent_mean_str
                nonviolent_std_str = nonviolent_std_str + "}"
            if violent_mean == max(violent_means[:-1]):
                violent_mean_str = r"\textbf{" + violent_mean_str
                violent_std_str = violent_std_str + "}"
            if nuclear_mean == max(nuclear_means[:-1]):
                nuclear_mean_str = r"\textbf{" + nuclear_mean_str
                nuclear_std_str = nuclear_std_str + "}"
            if nonviolent_count_mean == max(nonviolent_counts_mean[:-1]):
                nonviolent_count_mean_str = (
                    r"\textbf{" + nonviolent_count_mean_str + "}"
                )
            if violent_count_mean == max(violent_counts_mean[:-1]):
                violent_count_mean_str = r"\textbf{" + violent_count_mean_str + "}"
            if nuclear_count_mean == max(nuclear_counts_mean[:-1]):
                nuclear_count_mean_str = r"\textbf{" + nuclear_count_mean_str + "}"

            scenario_str = scenario if "GPT-4" in model_name else ""
            row = rf"        {scenario_str} & {model_name} & {nonviolent_mean_str} $\pm$ {nonviolent_std_str}\% {nonviolent_count_mean_str} & {violent_mean_str} $\pm$ {violent_std_str}\% {violent_count_mean_str} & {nuclear_mean_str} $\pm$ {nuclear_std_str}\% {nuclear_count_mean_str} & TEMP $\pm$ TEMP \\"
            if model_name == "GPT-4-Base":
                # Hold out to print at the end
                gpt_4_base_rows += row + "\n"
            else:
                print(row)
        print("        \\hline")
    print("        \\hline")
    print(gpt_4_base_rows + "        \\hline")
    print("    \\end{tabularx}")

    # Plot a bunch of different bar graphs for different combos of models
    for model_name in ALL_MODEL_NAMES_WITH_GPT_4_BASE:
        if PLOT_NUMBER_TO_CREATE >= 4 or PLOT_NUMBER_TO_CREATE == 0:
            continue

        # Create a DF of the counts of each model/scenario/action combo in each file
        print("Counting actions...")
        graphing_data_actions = []
        for df in dfs_list:
            if df["model_name"].unique()[0] != model_name:
                continue
            for scenario in ALL_SCENARIOS:
                for action in ACTION_ORDER:
                    count = (
                        len(df[(df["scenario"] == scenario) & (df["action"] == action)])
                        / 8
                    )  # Divide by 8 nations
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

        # Create a similar DF but by severity rather than actions
        groups_by_severity = [
            df.groupby(
                ["day", "model_name", "scenario", "severity"], observed=True
            ).size()
            for df in dfs_list
            if df["model_name"].unique()[0] == model_name
        ]
        # Manually add in 0 counts for missing severities each day
        for i, series in enumerate(groups_by_severity):
            scenario = dfs_list[i]["scenario"].unique()[0]
            for day in range(1, 15):
                for severity in SEVERITIES_ORDER:
                    grouping = (day, model_name, scenario, severity)
                    if grouping not in series:
                        groups_by_severity[i][grouping] = 0
        graphing_data_severities = []
        for series in groups_by_severity:
            for (day, series_model_name, scenario, severity), count in series.items():
                count /= 8  # Divide by 8 nations
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

        # 1. Multi-line plot of severities over time
        if PLOT_NUMBER_TO_CREATE == 1:
            # Create a 1x3 subplot with shared y-axis and y-label
            initialize_plot_default()
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))  # , sharey=True)
            fig.subplots_adjust(wspace=0.125)
            # Add padding to the bottom without subplots_adjust
            fig.tight_layout(h_pad=10.0)

            for i, scenario in enumerate(ALL_SCENARIOS):
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

                ax = axes[i]
                x_variable = "day"
                y_variable = "count"
                x_label = TIMELABEL_DEFAULT
                y_label = "Mean Action Count per Nation" if i == 0 else None
                grouping = "severity"
                # Plot df_grouped
                sns.lineplot(
                    ax=ax,
                    data=df_plot,
                    x=x_variable,
                    y=y_variable,
                    hue=grouping,
                    style=grouping,
                    hue_order=SEVERITIES_ORDER,
                    markers=SEVERITY_TO_MARKER,
                    palette=SEVERITIES_TO_COLORS,
                )
                ax.legend().remove()  # We save the legend separately
                ax.set_xlabel(x_label, size=LABELSIZE_DEFAULT)
                ax.set_ylabel(y_label, size=LABELSIZE_DEFAULT)
                ax.set_yscale("log")
                ax.set_ylim(bottom=0.005, top=3)
                # Y axis ticks in non-scientific notation
                ax.set_yticks(
                    [0.01, 0.03, 0.1, 0.3, 1],
                    ["0.01", "0.03", "0.1", "0.3", "1"],
                    size=LABELSIZE_DEFAULT,
                )
                xticks = list(range(2, 15, 2))
                ax.set_xticks(ticks=xticks, labels=xticks, size=LABELSIZE_DEFAULT)
                title = f"{scenario} Scenario"
                ax.set_title(title)

            # Add a legend to the bottom of the plot without changing the relative sizing of the plots
            artists = axes[-1].get_legend_handles_labels()
            plt.figlegend(
                *artists,
                loc="lower center",
                ncol=6,
                framealpha=1.0,
                borderaxespad=0.0,
                borderpad=0.5,
                bbox_to_anchor=(0.5, -0.08),
            )
            plt.suptitle(f"{model_name} Action Severities Over Time", y=1.06)

            save_plot(
                OUTPUT_DIR_ACTIONS_OVER_TIME, f"{model_name} Action Severities All"
            )

        if PLOT_NUMBER_TO_CREATE == 2:
            # 2. Bar plot showing names grouped by scenario and for each model
            initialize_plot_bar()

            plt.figure(figsize=(15, 5))

            x_variable = "action"
            x_label = "Action"
            y_variable = "count"
            y_label = "Mean Action Count per Nation"
            grouping = "scenario"
            grouping_order = ALL_SCENARIOS
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
            plt.xticks(
                rotation=90,
            )

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
            yticks = [0.003, 0.01, 0.03, 0.1, 0.3, 1, 3, 10]
            plt.yticks(yticks, yticks, size=LABELSIZE_DEFAULT)

            title = f"{model_name} Distribution of All {len(ACTION_ORDER)} Actions by Scenario"
            plt.title(model_name)
            plt.legend(title="Scenario", loc="upper right", framealpha=0.5)

            save_plot(OUTPUT_DIR_DISTRIBUTIONS_ALL_ACTIONS, title)

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
                plt.figure(figsize=(8, 5))

                x_variable = "severity"
                x_label = "Severity of Action"
                y_variable = "count"
                y_label = "Mean Action Count per Nation"
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
                    capsize=CAPSIZE_DEFAULT,
                    errorbar="ci",
                    palette=palette,
                )
                plt.xlabel(x_label)
                # Ticks on the x axis
                plt.xticks(
                    list(range(0, len(SEVERITIES_ORDER_NEWLINES))),
                    labels=SEVERITIES_ORDER_NEWLINES,
                )
                plt.ylabel(y_label)
                plt.yscale("log")
                # Y axis labels in non-scientific notation
                plt.yticks(
                    [1, 3, 10, 30],
                    ["1", "3", "10", "30"],
                )

                title = f"{model_name} Action Severity Counts by {grouping_label} ({scenario} Scenario)"
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
            df.groupby(["model_name", "scenario", "severity"], observed=False).size()
            for df in dfs_list
        ]
        graphing_data_actions_all_models = []
        for series in groups_by_action_all_models:
            for (
                series_model_name,
                scenario,
                severity,
            ), count in series.items():
                count /= 8  # Divide by 8 nations
                graphing_data_actions_all_models.append(
                    {
                        "model_name": series_model_name,
                        "scenario": scenario,
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
            plt.figure(figsize=(8, 5))
            x_variable = "severity"
            x_label = "Severity of Action"
            y_variable = "count"
            y_label = "Mean Action Count per Nation"
            grouping = "model_name"
            grouping_order = ALL_MODEL_NAMES
            sns.barplot(
                data=df_plot,
                x=x_variable,
                y=y_variable,
                order=SEVERITIES_ORDER,
                hue=grouping,
                hue_order=grouping_order,
                capsize=CAPSIZE_DEFAULT,
                errorbar="ci",
                palette=MODELS_TO_COLORS,
            )
            plt.xlabel(x_label)
            plt.xticks(
                list(range(0, len(SEVERITIES_ORDER_NEWLINES))),
                labels=SEVERITIES_ORDER_NEWLINES,
            )
            plt.ylabel(y_label)
            plt.yscale("log")
            # Y axis labels in non-scientific notation
            yticks = [0.03, 0.1, 0.3, 1, 3, 10, 30]
            plt.yticks(yticks, yticks, size=LABELSIZE_DEFAULT)

            title = f"Severity of Actions by Model ({scenario} Scenario)"
            plt.title(title)
            plt.legend(
                title="Model",
                loc="best",
                framealpha=0.5,
                borderaxespad=0.0,
                handletextpad=0.1,
                labelspacing=0.25,
            )

            save_plot(OUTPUT_DIR_SEVERITY_BY_MODEL, title)

            # Clear the plot
            plt.clf()
            del df_plot

    if PLOT_NUMBER_TO_CREATE == 5:
        # 5. Severities of Actions by Model (but with GPT-4-Base and wider)
        groups_by_action_all_models = [
            df.groupby(["model_name", "scenario", "severity"], observed=False).size()
            for df in dfs_list
        ]
        graphing_data_actions_all_models = []
        for series in groups_by_action_all_models:
            for (
                series_model_name,
                scenario,
                severity,
            ), count in series.items():
                count /= 8  # Divide by 8 nations
                graphing_data_actions_all_models.append(
                    {
                        "model_name": series_model_name,
                        "scenario": scenario,
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
            plt.figure(figsize=(10, 5))
            x_variable = "severity"
            x_label = "Severity of Action"
            y_variable = "count"
            y_label = "Mean Action Count per Nation"
            grouping = "model_name"
            grouping_order = ALL_MODEL_NAMES_WITH_GPT_4_BASE
            sns.barplot(
                data=df_plot,
                x=x_variable,
                y=y_variable,
                order=SEVERITIES_ORDER,
                hue=grouping,
                hue_order=grouping_order,
                capsize=CAPSIZE_DEFAULT,
                errorbar="ci",
                palette=MODELS_TO_COLORS,
            )
            plt.xlabel(x_label)
            plt.xticks(
                list(range(0, len(SEVERITIES_ORDER_NEWLINES))),
                labels=SEVERITIES_ORDER_NEWLINES,
                size=LABELSIZE_DEFAULT,
            )
            plt.ylabel(y_label)
            plt.yscale("log")
            yticks = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30]
            plt.yticks(yticks, yticks, size=LABELSIZE_DEFAULT)

            title = f"Severity of Actions by Model ({scenario} Scenario)"
            plt.title(f"{scenario} Scenario")
            plt.legend(
                # title="Model",
                loc="upper right",
                # framealpha=0.5,
                borderaxespad=0.0,
                handletextpad=0.1,
                labelspacing=0.25,
            )

            save_plot(OUTPUT_DIR_SEVERITY_BY_MODEL, "full_" + title)
            plt.clf()
            del df_plot

    # 1x4 action severities over time plot row
    if PLOT_NUMBER_TO_CREATE == 6:
        graphing_data_actions = []
        for model_name in ALL_MODEL_NAMES:
            # Create a DF of the counts of each model/scenario/action combo in each file
            print("Counting actions...")
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

        # Create a DF but by severity rather than actions
        groups_by_severity = [
            df.groupby(
                ["day", "model_name", "scenario", "severity"], observed=True
            ).size()
            for df in dfs_list
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

        for scenario in ALL_SCENARIOS:
            _, axes = plt.subplots(
                nrows=1, ncols=4, figsize=(14, 3.5)
            )  # Adjust figsize as needed

            x_variable = "day"
            y_variable = "count"

            for i, model_name in enumerate(ALL_MODEL_NAMES[::-1]):
                # Filter data for the current model
                df_plot = df_severities[
                    df_severities["model_name"] == model_name
                ].copy()
                df_plot = df_plot[df_plot["scenario"] == scenario].copy()

                grouping = "severity"
                initialize_plot_default()
                sns.lineplot(
                    ax=axes[i],
                    data=df_plot,
                    x=x_variable,
                    y=y_variable,
                    hue=grouping,
                    style=grouping,
                    hue_order=SEVERITIES_ORDER,
                    markers=SEVERITY_TO_MARKER,
                    palette=SEVERITIES_TO_COLORS,
                )
                axes[i].set_title(f"{model_name}")
                axes[i].set_xlabel(TIMELABEL_DEFAULT)
                ylabel = "Daily Action Count" if i == 0 else ""
                axes[i].set_ylabel(ylabel)
                axes[i].set_yscale("log")
                # Y axis ticks in non-scientific notation
                axes[i].set_yticks(
                    [1, 3, 10, 30],
                    ["1", "3", "10", "30"],
                )
                # No legend
                axes[i].legend().remove()
                axes[i].grid(True, alpha=0.5)

            # Add a legend to the bottom of the plot without changing the relative sizing of the plots
            # axes[0].legend(
            #     loc="upper center",
            #     bbox_to_anchor=(0.5, -0.2),
            #     ncol=6,
            #     framealpha=0.5,
            #     borderaxespad=0.0,
            # )
            artists = axes[-1].get_legend_handles_labels()
            plt.figlegend(
                *artists,
                loc="lower center",
                ncol=6,
                framealpha=0.5,
                borderaxespad=0.0,
            )

            title = f"Multiple_graph_action_severities_{scenario}"
            plt.tight_layout()
            save_plot(OUTPUT_DIR_ACTIONS_OVER_TIME, title)
            plt.close()
            plt.clf()
            del title

    # 1x4 total num actions over time plot row, not grouped by severity
    if PLOT_NUMBER_TO_CREATE == 7:
        # Create a DF with the total counts per day
        grouped = [
            df.groupby(["day", "model_name", "scenario"], observed=True).size()
            for df in dfs_list
        ]
        graphing_data = []
        for series in grouped:
            for (day, series_model_name, scenario), count in series.items():
                count /= 8  # Divide by 8 nations
                graphing_data.append(
                    {
                        "day": day,
                        "model_name": series_model_name,
                        "scenario": scenario,
                        "count": count,
                    }
                )
        df_actions = pd.DataFrame(graphing_data)

        for model_name in ALL_MODEL_NAMES_WITH_GPT_4_BASE:
            initialize_plot_default()
            _, axes = plt.subplots(nrows=1, ncols=3, figsize=(14, 4))

            x_variable = "day"
            y_variable = "count"
            y_label = "Total Action Count Per Nation"
            for i, scenario in enumerate(ALL_SCENARIOS):
                # Filter data for the current model
                df_plot = df_actions[df_actions["model_name"] == model_name].copy()
                df_plot = df_plot[df_plot["scenario"] == scenario].copy()

                sns.lineplot(
                    ax=axes[i],
                    data=df_plot,
                    x=x_variable,
                    y=y_variable,
                    markers=True,
                    color=MODELS_TO_COLORS[model_name],
                    label=f"{model_name} {scenario} Scenario",
                )
                # Make sure label is in upper left
                handles, labels = axes[i].get_legend_handles_labels()
                axes[i].legend(handles[::-1], labels[::-1], loc="upper left")

                # axes[i].set_title(f"{model_name}")
                axes[i].set_xlabel(TIMELABEL_DEFAULT, size=LABELSIZE_DEFAULT)
                ylabel_sub = y_label if i == 0 else ""
                axes[i].set_ylabel(ylabel_sub, size=LABELSIZE_DEFAULT)
                axes[i].set_ylim(1.25, 10)
                axes[i].grid(True, alpha=0.5)

            title = f"{model_name} {y_label} Over Time"
            plt.suptitle(title, y=0.95)
            plt.tight_layout()
            save_plot(OUTPUT_DIR_ACTIONS_OVER_TIME, title)
            plt.close()
            plt.clf()
            del title


if __name__ == "__main__":
    if PLOT_NUMBER_TO_CREATE == -1:
        # Run all plot indices:
        for i in range(8):
            PLOT_NUMBER_TO_CREATE = i
            main()
    else:
        main()
