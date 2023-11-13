"""
Charts for scores over time
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from chart_utils import (
    ALL_MODEL_NAMES,
    ALL_MODEL_NAMES_WITH_GPT_4_BASE,
    ALL_SCENARIOS,
    ALL_DYNAMIC_VARIABLES,
    DYNAMIC_VARIABLES_TO_NAMES,
    MODELS_TO_COLORS,
    MODELS_TO_MARKERS,
    initialize_plot_default,
    initialize_plot_bar,
    save_plot,
    get_results_full_path,
)

INPUT_DIR = "../results/variables_v3"
OUTPUT_DIR = "./dynamic_variables"

INDEX_TO_CREATE = 2


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
            scenario=filename.split(" ")[1],
        )
        for filename, df in filenames_and_data
    ]
    df_all = pd.concat(dfs_list)

    # Change all the 0 days to 1 due to a logging issue
    df_all.loc[df_all["day"] == 0, "day"] = 1

    # Drop the claude-1.2 data
    df_all = df_all[df_all["model_name"] != "Claude-1.2"].copy()

    # Drop data where model name not in ALL_MODEL_NAMES_WITH_GPT_4_BASE
    df_all = df_all[df_all["model_name"].isin(ALL_MODEL_NAMES_WITH_GPT_4_BASE)].copy()

    # Print how many runs there are for each model_name, scenario combo
    print("Runs per model_name, scenario combo:")
    print(df_all.groupby(["model_name", "scenario"]).size())

    if INDEX_TO_CREATE == 1:
        # Graph dynamic vars (e.g. population, military capacity) over time by models (hue) and scenario (plot)
        for scenario in ALL_SCENARIOS:
            for dynamic_variable in ALL_DYNAMIC_VARIABLES:
                # Filter dataframe to only include the current scenario and dynamic_variable
                df_filtered = df_all[(df_all["scenario"] == scenario)].copy()
                # Filter out GPT-4 base and only use ALL_MODEL_NAMES
                df_filtered = df_filtered[
                    (df_filtered["model_name"].isin(ALL_MODEL_NAMES))
                ].copy()
                if len(df_filtered) == 0:
                    print(
                        f"No data for {scenario} scenario and {dynamic_variable} variable"
                    )
                    continue

                initialize_plot_default()
                plt.rcParams["figure.figsize"] = (7, 5)
                grouping = "model_name"
                x_variable = "day"
                x_label = "Day"
                assert (
                    "_dynamic" in dynamic_variable
                ), f"dynamic variable={dynamic_variable} (expected to contain '_dynamic')"
                y_variable = dynamic_variable.split("_dynamic")[0].replace("_", " ")
                y_label = "Average " + DYNAMIC_VARIABLES_TO_NAMES[dynamic_variable]
                grouping_order = ALL_MODEL_NAMES
                # Plot df_grouped
                sns.lineplot(
                    data=df_filtered,
                    x=x_variable,
                    y=y_variable,
                    hue=grouping,
                    style=grouping,
                    # hue_order=grouping_order,
                    # ci=None,
                    palette=MODELS_TO_COLORS,
                    hue_order=ALL_MODEL_NAMES,
                    markers=MODELS_TO_MARKERS,
                )
                plt.xlabel(x_label)
                plt.ylabel(y_label)
                # plt.yscale("log")
                title = f"{y_label.replace('Average ', '')} Over Time in {scenario} Scenario"
                plt.title(title)

                plt.legend(
                    # bbox_to_anchor=(1.05, 1),
                    loc="best",
                    borderaxespad=0.0,
                    ncol=2,
                    title="Model",
                    handletextpad=0.1,
                    labelspacing=0.25,
                    framealpha=0.5,
                    columnspacing=0.25,
                )

                # Save the plot
                save_plot(OUTPUT_DIR, title)

                # Clear the plot
                plt.clf()

    # Plot a bunch of different bar graphs for different combos of models
    for model_name in ["GPT-4-Base"] + ALL_MODEL_NAMES + ["All Models"]:
        # Filter dataframe to only include the current model
        if model_name == "All Models":
            df_model = df_all.copy()
        else:
            df_model = df_all[df_all["model_name"] == model_name].copy()

        # 1. Multi-line plot of all variables over time
        columns_of_interest = [
            "day",
            "scenario",
            "military capacity",
            "gdp",
            "trade",
            "resources",
            "political stability",
            # "population",
            "soft power",
            "cybersecurity",
            "nuclear",
        ]
        df_plot = df_model[columns_of_interest].copy()
        # Create a new DF where the non-[day or scenario] columns are the "variable" column
        df_plot = df_plot.melt(
            id_vars=["day", "scenario"],
            var_name="variable",
            value_name="value",
        )
        if INDEX_TO_CREATE == 2:
            # Filter by scenario
            for scenario in ALL_SCENARIOS:
                df_filtered = df_plot[df_plot["scenario"] == scenario].copy()
                if len(df_filtered) == 0:
                    print(f"No data for {scenario} scenario and {model_name} model")
                    continue

                # Rename variables to be prettier
                df_filtered["variable"] = df_filtered["variable"].apply(
                    lambda x: DYNAMIC_VARIABLES_TO_NAMES[
                        x.replace(" ", "_") + "_dynamic"
                    ].replace(" ", "\n")
                )

                initialize_plot_default()
                plt.rcParams["figure.figsize"] = (12, 6)
                grouping = "variable"
                x_variable = "day"
                x_label = "Day"
                y_label = "Dynamic Variable Value"
                grouping_order = ALL_SCENARIOS
                # Plot df_grouped
                sns.lineplot(
                    data=df_filtered,
                    x=x_variable,
                    y="value",
                    hue=grouping,
                    style=grouping,
                    markers=True,
                    errorbar="ci",
                )
                plt.xlabel(x_label)
                plt.ylabel(y_label)
                # plt.yscale("log")
                ticks = [5, 10, 15, 20, 25, 30]
                # plt.yticks(ticks, [str(tick) for tick in ticks])
                title = (
                    f"Dynamic Variables Over Time in {scenario} Scenario ({model_name})"
                )
                plt.title(title)
                # Legend to the right of the plot
                plt.legend(
                    bbox_to_anchor=(1.01, 1),
                    loc="upper left",
                    borderaxespad=0.0,
                    ncol=1,
                    title="Variable",
                    handletextpad=0.1,
                    labelspacing=0.5,
                    framealpha=0.5,
                    columnspacing=0.25,
                    # map={
                    #     variable: DYNAMIC_VARIABLES_TO_NAMES[variable]
                    #     for variable in ALL_DYNAMIC_VARIABLES
                    # },
                )

                # Save the plot
                save_plot(OUTPUT_DIR, title)

                # Clear the plot
                plt.clf()

                # exit()  # DEBUG

        if INDEX_TO_CREATE == 3:
            # Next: Bar plot of the value of each variable for each scenario
            # First, filter to day=15 to get the end
            df_plot_2 = df_plot[df_plot["day"] == 15].copy()
            # Drop day column
            df_plot_2 = df_plot_2.drop(columns=["day"])
            # Plot, using variable as x axis and scenario as grouping
            initialize_plot_bar()
            plt.rcParams["figure.figsize"] = (16, 6)
            grouping = "scenario"
            x_variable = "variable"
            x_label = "Variable"
            y_label = "Value"
            grouping_order = ALL_SCENARIOS
            # Plot df_grouped
            sns.barplot(
                data=df_plot_2,
                x=x_variable,
                y="value",
                hue=grouping,
                # order=df_grouped.index.get_level_values(x_variable).unique(),
                hue_order=grouping_order,
            )
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            # plt.yscale("log")
            title = f"Final Nation Variables by Scenario ({model_name})"
            plt.title(title)

            # Save the plot
            save_plot(OUTPUT_DIR, title)

            # Clear the plot
            plt.clf()


if __name__ == "__main__":
    main()
