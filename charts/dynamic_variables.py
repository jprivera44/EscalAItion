"""
Charts for scores over time
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from chart_utils import (
    ALL_MODEL_NAMES,
    initialize_plot_default,
    initialize_plot_bar,
    save_plot,
    get_results_full_path,
)

INPUT_DIR = "../results/variables"
OUTPUT_DIR = "./variables"


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

    # # Print how many runs there are for each model_name, scenario combo
    # print("Runs per model_name, year_integer combo:")
    # print(df_all.groupby(["model_name", "scenario"]).size())

    # # Print how many rows for each model_name, action combo
    # print("Rows per model_name, action combo:")
    # print(df_all.groupby(["model_name", "action"]).size())

    # Plot a bunch of different bar graphs for different combos of models
    for model_name in ALL_MODEL_NAMES + ["All Models"]:
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
        # Filter by scenario
        for scenario in ["Neutral", "Drone"]:
            df_filtered = df_plot[df_plot["scenario"] == scenario].copy()
            if len(df_filtered) == 0:
                continue

            initialize_plot_default()
            # plt.rcParams["figure.figsize"] = (16, 6)
            grouping = "variable"
            x_variable = "day"
            x_label = "Day"
            y_label = "Value"
            grouping_order = ["Neutral", "Drone"]
            # Plot df_grouped
            sns.lineplot(
                data=df_filtered,
                x=x_variable,
                y="value",
                hue=grouping,
                # hue_order=grouping_order,
                # ci=None,
            )
            plt.xlabel(x_label)
            plt.xticks(rotation=25)
            plt.ylabel(y_label)
            plt.yscale("log")
            title = f"Nation Variables for {scenario} Scenario ({model_name})"
            plt.title(title)

            # Save the plot
            output_file = get_results_full_path(
                os.path.join(OUTPUT_DIR, f"{title}.png")
            )
            save_plot(output_file)
            print(f"Saved plot '{title}' to {output_file}")

            # Clear the plot
            plt.clf()

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
        grouping_order = ["Neutral", "Drone"]
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
        plt.xticks(rotation=30)
        plt.ylabel(y_label)
        plt.yscale("log")
        title = f"Final Nation Variables by Scenario ({model_name})"
        plt.title(title)

        # Save the plot
        output_file = get_results_full_path(os.path.join(OUTPUT_DIR, f"{title}.png"))
        save_plot(output_file)
        print(f"Saved plot '{title}' to {output_file}")


if __name__ == "__main__":
    main()
