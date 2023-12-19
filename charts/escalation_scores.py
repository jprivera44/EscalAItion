"""
Charts for action history.
"""

import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from chart_utils import (
    ALL_SCENARIOS,
    # SCENARIOS_TO_COLORS,
    MODELS_TO_MARKERS,
    MODELS_TO_COLORS,
    # CAPSIZE_DEFAULT,
    ALL_MODEL_NAMES,
    ALL_MODEL_NAMES_WITH_GPT_4_BASE,
    TIMELABEL_DEFAULT,
    initialize_plot_default,
    # initialize_plot_bar,
    save_plot,
    get_results_full_path,
    # get_color_from_palette,
)

file_eval_type = "exponential"

# INPUT_DIR = "../evals/json_by_color_v4_" + file_eval_type
INPUT_DIR = "../evals/json_v4_" + file_eval_type
# OUTPUT_DIR = "./escalation_scores_by_color" + file_eval_type + "_2x4"
OUTPUT_DIR = "./escalation_scores_v6"

PLOT_NUMBER_TO_CREATE = 3


def main() -> None:
    """Main function."""

    # colors = ["White", "Yellow", "Blue", "Green", "Pink", "Purple", "Red", "Orange"]  # List your colors here

    # for color in colors:
    # TODO @JP you broke all the past graphs by doing this, please
    # 1) only push code that works and
    # 2) make your code modular so we can still run the old graphs if we need to update them

    # filenames_and_data = []
    # for filename in os.listdir(get_results_full_path(INPUT_DIR)):
    #     if f"_{color}_" in filename:
    #         df = load_json_data(get_results_full_path(os.path.join(INPUT_DIR, filename)), color)
    #         filenames_and_data.append((filename, df))

    # TODO @JP this is bad code smell, 1) use # not ''' for commenting things out and 2) avoid pushing commented out code
    # '''
    # # Load the data from each file into one big dataframe
    # filenames_and_data = [
    #     (
    #         filename,
    #         load_json_data(get_results_full_path(os.path.join(INPUT_DIR, filename))),
    #     )
    #     for filename in os.listdir(get_results_full_path(INPUT_DIR))
    # ]
    # '''

    # # Concatenate all dataframes for the current color
    # dfs_list = [
    #     df.assign(
    #         model_name=filename.split(" ")[0],
    #         run_index=filename.replace(".json", "").replace("_raw", "")[-1],
    #         scenario=filename.split(" ")[1].replace("_", " ").replace("CyberAttack", "Cyberattack"),
    #     )
    #     for filename, df in filenames_and_data
    #     if filename.split(" ")[0] in ALL_MODEL_NAMES_WITH_GPT_4_BASE
    # ]

    # '''
    # # Create a concatted dataframe using filenames to add columns. Split filenames on spaces, then first element is model_name and second is scenario
    # dfs_list = [
    #     df.assign(
    #         model_name=filename.split(" ")[0],
    #         run_index=filename.replace(".json", "").replace("_raw", "")[-1],
    #         scenario=filename.split(" ")[1]
    #         .replace("_", " ")
    #         .replace("CyberAttack", "Cyberattack"),
    #     )
    #     for filename, df in filenames_and_data
    #     # Filter to model names in ALL_MODEL_NAMES
    #     if filename.split(" ")[0] in ALL_MODEL_NAMES_WITH_GPT_4_BASE
    # ]
    # '''

    # Load the data from each file into one big dataframe
    filenames_and_data = [
        (
            filename,
            load_json_data(get_results_full_path(os.path.join(INPUT_DIR, filename))),
        )
        for filename in os.listdir(get_results_full_path(INPUT_DIR))
    ]

    dfs_list = [
        df.assign(
            model_name=filename.split(" ")[0],
            run_index=filename.replace(".json", "").replace("_raw", "")[-1],
            scenario=filename.split(" ")[1]
            .replace("_", " ")
            .replace("CyberAttack", "Cyberattack"),
        )
        for filename, df in filenames_and_data
        # Filter to model names in ALL_MODEL_NAMES
        if filename.split(" ")[0] in ALL_MODEL_NAMES_WITH_GPT_4_BASE
    ]

    # Print how many runs there are for each model_name, scenario combo
    print("Runs per model_name, scenario combo:")
    print(pd.concat(dfs_list).groupby(["model_name", "scenario"]).size())

    # Print average escalation score for each model_name, scenario combo
    print("Average escalation score per model_name, scenario combo:")

    print(
        pd.concat(dfs_list)
        .groupby(["model_name", "scenario"])["total"]
        .mean()
        # Format to 2 decimal places
        .apply(lambda x: round(x, 2))
    )

    # For each scenario, for each model, print avg and std escalation scores (for main comparison table)
    print("\nMain Table Escalation Score Data")
    for scenario in ALL_SCENARIOS:
        df_list_scenario = [
            df for df in dfs_list if df["scenario"].unique()[0] == scenario
        ]
        mean_per_run_list = []
        stdper_run_list = []
        for model_name in ALL_MODEL_NAMES_WITH_GPT_4_BASE:
            df_list_model = [
                df
                for df in df_list_scenario
                if df["model_name"].unique()[0] == model_name
            ]
            # Mean escalation score within each run
            run_mean_scores = [(np.mean(df["total"])) for df in df_list_model]
            mean_per_run_list.append(np.mean(run_mean_scores))
            stdper_run_list.append(np.std(run_mean_scores))

        for i, model_name in enumerate(ALL_MODEL_NAMES_WITH_GPT_4_BASE):
            score_mean = mean_per_run_list[i]
            score_std = stdper_run_list[i]
            score_mean_str = f"{score_mean:.2f}"
            score_std_str = f"{score_std:.2f}"
            if score_mean == max(mean_per_run_list):
                score_mean_str = r"\textbf{" + score_mean_str + "}"
                score_std_str = r"\textbf{" + score_std_str + "}"

            print(
                rf"{scenario:11s} | {model_name:12s} | {score_mean_str} $\pm$ {score_std_str}"
            )

    print("\nLatex Table of beginning, middle, and end escalation scores (t=1, 8, 14)")
    # Print header
    print(
        r"    \begin{tabularx}{0.85\textwidth}{|c|c|X|X|X|} \hline"
        "\n"
        r"    \textbf{Scenario} & \textbf{Model} & \textbf{Escalation Score \newline Beginning ($t=1$)} & \textbf{Escalation Score \newline Middle ($t=8$)} & \textbf{Escalation Score \newline End ($t=14$)} \\ \hline"
    )
    gpt_4_base_rows = ""
    for scenario in ALL_SCENARIOS:
        df_list_scenario = [
            df for df in dfs_list if df["scenario"].unique()[0] == scenario
        ]
        for model_name in ALL_MODEL_NAMES_WITH_GPT_4_BASE:
            df_list_model = [
                df
                for df in df_list_scenario
                if df["model_name"].unique()[0] == model_name
            ]
            # Filter by day=1, 8, 14 and print mean and std ES across the 10 runs
            mean_mean_str_std_str: list[tuple[float, str, str]] = []
            for day in [1, 8, 14]:
                df_list_day = [df[df["day"] == day] for df in df_list_model]
                assert len(df_list_day) == 10, f"len(df_list_day) = {len(df_list_day)}"
                # Mean escalation score within each run
                run_mean_scores = [(np.mean(df["total"])) for df in df_list_day]
                mean = np.mean(run_mean_scores)
                std = np.std(run_mean_scores)
                mean_str = f"{mean:.2f}"
                std_str = f"{std:.2f}"
                mean_mean_str_std_str.append((mean, mean_str, std_str))
            # Print full row, bolding the cell with the highest mean
            max_mean = max(mean_mean_str_std_str, key=lambda x: x[0])[0]
            scenario_str = scenario
            if "Llama" not in model_name and "Base" not in model_name:
                # Only print scenario once per group
                scenario_str = ""
            row = f"    {scenario_str:15s} & {model_name:12s}"
            for mean, mean_str, std_str in mean_mean_str_std_str:
                if mean == max_mean:
                    mean_str = r"\textbf{" + mean_str
                    std_str = std_str + "}"
                # Underline second highest
                elif mean == sorted(mean_mean_str_std_str)[-2][0]:
                    mean_str = r"\underline{" + mean_str
                    std_str = std_str + "}"
                row += rf" & {mean_str:13s} $\pm$ {std_str:6s}"
            row += r" \\[2.5pt]"
            # Save GPT-4-base to the end
            if model_name == "GPT-4-Base":
                gpt_4_base_rows += row + "\n"
            else:
                print(row)
        print(r"    \hline")
    print(
        r"    \hline\hline" + "\n" + gpt_4_base_rows + r"    \hline"
        "\n"
        r"    \end{tabularx}"
    )
    print("\n")

    if PLOT_NUMBER_TO_CREATE == 0:
        return

    for scenario in ALL_SCENARIOS:
        df_scenario = pd.concat(dfs_list).query(f"scenario == '{scenario}'")

        # Graph median escalation score simulations for each model together on a lineplot over time
        # To filter by median, we need to look at all runs per model, then calculate the sum of the "total" column for each run, then take only the run with the median of that sum
        dfs_to_keep = []
        for model_name in ALL_MODEL_NAMES:
            df_model = df_scenario.query(f"model_name == '{model_name}'").copy()
            # Calculate the sum of the "total" column for each run
            df_model["total_sum"] = df_model.groupby("run_index")["total"].transform(
                "sum"
            )
            # Get the run with the median of that sum
            median_total_sum = df_model["total_sum"].median()
            matched_run = df_model.query(f"total_sum == {median_total_sum}")
            if len(matched_run) == 0:
                # Harder: find the run with the closest total_sum to the median
                unique_total_sums = df_model["total_sum"].unique()
                closest_total_sum = min(
                    unique_total_sums, key=lambda x: abs(x - median_total_sum)  # type: ignore
                )
                matched_run = df_model.query(f"total_sum == {closest_total_sum}")
            dfs_to_keep.append(matched_run)
        df_plot = pd.concat(dfs_to_keep)

        if PLOT_NUMBER_TO_CREATE == 1:
            # Make the plot
            grouping = "model_name"
            initialize_plot_default()
            sns.lineplot(
                data=df_plot,
                x="day",
                y="total",
                hue=grouping,
                palette=MODELS_TO_COLORS,
                hue_order=ALL_MODEL_NAMES,
                dashes=False,
                style=grouping,
                markers=MODELS_TO_MARKERS,
            )
            plt.xlabel("Day")
            plt.ylabel("Escalation Score ←")
            title = f"Escalation Score Over Time for Median Simulation ({scenario} Scenario)"
            plt.title(title)
            plt.legend(
                loc="best",
                framealpha=0.5,
                borderaxespad=0.0,
                handletextpad=0.1,
                labelspacing=0.25,
            )
            save_plot(OUTPUT_DIR, title)
            plt.close()
            del dfs_to_keep, title

        elif PLOT_NUMBER_TO_CREATE == 2:
            # Now do a similar plot but with all data, not just median runs, so we get confidence intervals
            grouping = "model_name"
            initialize_plot_default()
            sns.lineplot(
                data=df_scenario,
                x="day",
                y="total",
                hue=grouping,
                palette=MODELS_TO_COLORS,
                hue_order=ALL_MODEL_NAMES,
                dashes=False,
                style=grouping,
                markers=MODELS_TO_MARKERS,
            )
            plt.xlabel("Day")
            plt.ylabel("Escalation Score ←")
            title = f"Average Escalation Score Over Time ({scenario} Scenario)"
            plt.title(title)

            legend_loc = "upper left"
            if scenario == "Invasion":
                legend_loc = "best"
            plt.legend(
                loc=legend_loc,
                framealpha=0.5,
                borderaxespad=0.0,
                handletextpad=0.1,
                labelspacing=0.25,
            )

            save_plot(OUTPUT_DIR, title)
            plt.close()
            del title

        # 3. grid of scores over time and differences over time
        elif PLOT_NUMBER_TO_CREATE >= 3:
            initialize_plot_default()
            # Calculate day-to-day differences
            df_scenario["daily_difference"] = (
                df_scenario.groupby(["model_name", "run_index", "scenario"])["total"]
                .diff()
                .fillna(0)
            )
            # Group by day and calculate mean and standard deviation
            stats_df = (
                df_scenario.groupby(["day", "model_name"])["daily_difference"]
                .agg(["mean", "std"])
                .reset_index()
            )

            # performing error checks on data, ensuring they are numeric and removal of inf values
            stats_df["day"] = pd.to_numeric(stats_df["day"], errors="coerce")
            stats_df["mean"] = pd.to_numeric(stats_df["mean"], errors="coerce")
            stats_df["std"] = pd.to_numeric(stats_df["std"], errors="coerce")
            stats_df.dropna(inplace=True)

            # For loop to plot the difference of mean - std, to show areas of variation
            for model in stats_df["model_name"].unique():
                model_data = stats_df[stats_df["model_name"] == model]
                plt.fill_between(
                    model_data["day"],
                    model_data["mean"] - model_data["std"],
                    model_data["mean"] + model_data["std"],
                    alpha=0.2,
                )

            # 1x4 grid showing individual runs
            if PLOT_NUMBER_TO_CREATE == 3:
                # Create a 5x2 grid of subplots
                _, axes = plt.subplots(
                    # nrows=2, ncols=4, figsize=(14, 7)
                    ncols=4,
                    figsize=(15, 5.4),
                )  # Adjust figsize as needed
                scenario_to_plot = df_scenario["scenario"].unique()[0]

                plt.suptitle(
                    f"Escalation Scores for All Runs over Time ({scenario_to_plot} Scenario)",
                    y=0.95,
                )

                for i, model in enumerate(ALL_MODEL_NAMES):
                    # Filter data for the current model
                    df_model_escalation = df_scenario[
                        df_scenario["model_name"] == model
                    ]
                    df_model_difference = stats_df[stats_df["model_name"] == model]

                    # Define the color for the current model
                    model_color = MODELS_TO_COLORS.get(
                        model, "black"
                    )  # Default to black if model not in dictionary

                    # Plot average escalation score in the first column
                    plt.rcParams["lines.marker"] = ""
                    sns.lineplot(
                        ax=axes[i],
                        x="day",
                        y="total",
                        hue="run_index",
                        data=df_model_escalation,
                        # color=model_color,
                        # palette=sns.color_palette("rocket"),
                        palette=sns.light_palette(model_color, n_colors=10),
                        marker=False,
                        errorbar=None,
                        # linestyle="dashed",
                        alpha=0.5,
                        legend=False,
                    )
                    sns.lineplot(
                        ax=axes[i],
                        x="day",
                        y="total",
                        data=df_model_escalation,
                        color=model_color,
                        linewidth=4.5,
                        errorbar=None,
                        label=model,
                    )
                    # legend in upper left
                    axes[i].legend(
                        loc="upper left",
                    )
                    axes[i].set_xlabel(TIMELABEL_DEFAULT)
                    ylabel = "Escalation Score" if i == 0 else ""
                    axes[i].set_ylabel(ylabel)
                    axes[i].set_ylim(-10, 350)

                title = (
                    "es_individual_runs_" + str(scenario_to_plot) + "_" + file_eval_type
                )
                plt.tight_layout()
                save_plot(OUTPUT_DIR, title)
                plt.close()
                plt.clf()
                del title

            # 4x2 grid of average escalation scores and differences over tizme
            elif PLOT_NUMBER_TO_CREATE == 4:
                # Create a 5x2 grid of subplots
                _, axes = plt.subplots(
                    # nrows=2, ncols=4, figsize=(14, 7)
                    nrows=5,
                    ncols=2,
                    figsize=(12, 16),
                )  # Adjust figsize as needed
                scenario_to_plot = df_scenario["scenario"].unique()[0]

                plt.suptitle(
                    f"Mean Escalation Scores and Turn-to-Turn Differences over Time ({scenario_to_plot} Scenario)"
                )

                for i, model in enumerate(ALL_MODEL_NAMES_WITH_GPT_4_BASE):
                    # Filter data for the current model
                    df_model_escalation = df_scenario[
                        df_scenario["model_name"] == model
                    ]
                    df_model_difference = stats_df[stats_df["model_name"] == model]

                    xlabel = "Day" if i == 3 else None

                    # Define the color for the current model
                    model_color = MODELS_TO_COLORS.get(
                        model, "black"
                    )  # Default to black if model not in dictionary

                    # Plot average escalation score in the first column
                    sns.lineplot(
                        ax=axes[i, 0],
                        x="day",
                        y="total",
                        data=df_model_escalation,
                        color=model_color,
                        label=f"{model} Mean",
                    )
                    # Label in upper left
                    axes[i, 0].legend(
                        loc="upper left",
                    )

                    axes[i, 0].set_xlabel(xlabel)
                    ylabel = "Escalation Score"
                    axes[i, 0].set_ylabel(ylabel)
                    axes[i, 0].set_ylim(0, 275)

                    # Plot average day-to-day differences in the second column
                    sns.lineplot(
                        ax=axes[i, 1],
                        x="day",
                        y="mean",
                        data=df_model_difference,
                        color=model_color,
                        label=f"{model} Differences",
                    )
                    # Label in upper left
                    axes[i, 1].legend(
                        loc="upper left",
                    )
                    axes[i, 1].set_xlabel(xlabel)
                    ylabel = "Turn-to-Turn Differences"
                    axes[i, 1].set_ylabel(ylabel)
                    axes[i, 1].set_ylim(-100, 100)

                    # Add fill_between for std deviation in day-to-day differences plot
                    axes[i, 1].fill_between(
                        df_model_difference["day"],
                        df_model_difference["mean"] - df_model_difference["std"],
                        df_model_difference["mean"] + df_model_difference["std"],
                        alpha=0.2,
                        color=model_color,
                    )

                title = (
                    "es_band_and_differences_"
                    + str(scenario_to_plot)
                    + "_"
                    + file_eval_type
                )
                plt.tight_layout()
                save_plot(OUTPUT_DIR, title)
                plt.close()
                plt.clf()
                del title


def load_json_data(filepath: str, color: str = "") -> pd.DataFrame:
    """Load the JSON of an escalation eval into a dataframe with [day, total] columns."""
    with open(filepath, encoding="utf-8") as file:
        json_data = json.load(file)
    data_rows = []
    for input_row in json_data:
        day = input_row["Day"]
        total = int(input_row["Total"])
        data_rows.append({"day": day, "total": total})
    df = pd.DataFrame(data_rows)
    return df


if __name__ == "__main__":
    main()
