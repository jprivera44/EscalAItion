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
    LABELSIZE_DEFAULT,
    MODELS_TO_COLORS,
    MODELS_TO_MARKERS,
    TIMELABEL_DEFAULT,
    initialize_plot_default,
    initialize_plot_bar,
    save_plot,
    get_results_full_path,
)

INPUT_DIR = "../results/variables_v3"
OUTPUT_DIR = "./dynamic_variables"

PLOT_NUMBER_TO_CREATE = 1


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
    dfs_list_unprocessed = [
        df.assign(
            model_name=filename.split(" ")[0],
            scenario=filename.split(" ")[1].replace("CyberAttack", "Cyberattack"),
        )
        for filename, df in filenames_and_data
    ]
    # For each df, average the dynamic variables for each day first, that way we normalize differences between nations but still get run error bands
    print("Averaging dynamic variables for each day...")
    columns = dfs_list_unprocessed[0].columns
    dfs_list = []
    for df_unprocessed in dfs_list_unprocessed:
        new_rows = []
        for day in range(0, 16):
            df_day = df_unprocessed[df_unprocessed["day"] == day].copy()
            if day == 1:
                continue  # Naming error
            elif day == 0:
                df_day["day"] = 1
            if len(df_day) == 0:
                print(f"⚠️ No data for day {day} in {df_unprocessed['model_name']}")
                continue
            averaged_values = []
            for column in columns:
                # Check if numeric
                if pd.api.types.is_numeric_dtype(df_day[column]):
                    # Average the values
                    averaged_values.append(df_day[column].mean())
                else:
                    # Append the first value
                    averaged_values.append(df_day[column].iloc[0])
            new_row = pd.Series(averaged_values, index=columns)
            new_rows.append(new_row)
        df_processed = pd.DataFrame(new_rows)
        dfs_list.append(df_processed)
    # Concat the dfs
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

    if PLOT_NUMBER_TO_CREATE == 1:
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
                plt.figure(figsize=(7, 5))
                grouping = "model_name"
                x_variable = "day"
                x_label = TIMELABEL_DEFAULT
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
                plt.xlabel(x_label, size=LABELSIZE_DEFAULT)
                plt.ylabel(y_label, size=LABELSIZE_DEFAULT)
                # plt.yscale("log")
                title = f"{y_label.replace('Average ', '')} ({scenario} Scenario)"
                plt.title(title)

                loc = (
                    "lower left"
                    if dynamic_variable == "population_dynamic"
                    else "upper left"
                )
                plt.legend(
                    # bbox_to_anchor=(1.05, 1),
                    loc=loc,
                    borderaxespad=0.0,
                    # ncol=2,
                    title="Model",
                    handletextpad=0.1,
                    labelspacing=0.25,
                    # framealpha=0.5,
                    columnspacing=0.25,
                )

                # Save the plot
                save_plot(
                    OUTPUT_DIR,
                    f"Var_{DYNAMIC_VARIABLES_TO_NAMES[dynamic_variable]}_{scenario}",
                )

                # Clear the plot
                plt.clf()
                plt.close()

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
            "population",
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
        # Divide the population rows by a constant so they fit
        population_divisor = 25
        df_plot.loc[df_plot["variable"] == "population", "value"] = (
            df_plot[df_plot["variable"] == "population"]["value"] / population_divisor
        )
        if PLOT_NUMBER_TO_CREATE == 2:
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
                    ]
                    .replace(" ", "\n")
                    .replace("Population", f"Population\n$\div$ {population_divisor}")  # type: ignore
                )

                initialize_plot_default()
                plt.figure(figsize=(12, 6))
                grouping = "variable"
                x_variable = "day"
                x_label = TIMELABEL_DEFAULT
                y_label = "Dynamic Variable Averaged Across Nations"
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
                plt.xlabel(x_label, size=LABELSIZE_DEFAULT)
                plt.ylabel(y_label, size=LABELSIZE_DEFAULT)
                title = (
                    f"{model_name} Dynamic Variables Over Time ({scenario} Scenario)"
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

        if PLOT_NUMBER_TO_CREATE == 3:
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
            plt.xlabel(x_label, size=LABELSIZE_DEFAULT)
            plt.ylabel(y_label, size=LABELSIZE_DEFAULT)
            # plt.yscale("log")
            title = f"Final Nation Variables by Scenario ({model_name})"
            plt.title(title)

            # Save the plot
            save_plot(OUTPUT_DIR, title)

            # Clear the plot
            plt.clf()


if __name__ == "__main__":
    if PLOT_NUMBER_TO_CREATE == -1:
        # Run all plot indices:
        for i in range(6):
            PLOT_NUMBER_TO_CREATE = i
            main()
    else:
        main()
