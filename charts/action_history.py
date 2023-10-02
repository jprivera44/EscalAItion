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

INPUT_DIR = "../results/actions"
OUTPUT_DIR = "./actions"


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
    # Create a concatted dataframe using filenames to add columns. Split filenames on spaces, then first element is model_name and second is situation
    dfs_list = [
        df.assign(
            model_name=filename.split(" ")[0],
            situation=filename.split(" ")[1],
        )
        for filename, df in filenames_and_data
    ]
    df_all = pd.concat(dfs_list)

    # # Print how many runs there are for each model_name, situation combo
    # print("Runs per model_name, year_integer combo:")
    # print(df_all.groupby(["model_name", "situation"]).size())

    # # Print how many rows for each model_name, action combo
    # print("Rows per model_name, action combo:")
    # print(df_all.groupby(["model_name", "action"]).size())

    # Plot a bunch of different bar graphs for different combos of models
    for model_name in ALL_MODEL_NAMES + ["All Models"]:
        # Filter dataframe to only include the current model
        if model_name == "All Models":
            df_plot = df_all.copy()
        else:
            df_plot = df_all[df_all["model_name"] == model_name].copy()

        # 1. Countplot of action names grouped by situation
        # Create a DF of the counts of each model/situation/action combo in each file
        groups_sizes = [
            df.groupby(["model_name", "situation", "action"]).size()
            for df in dfs_list
            if df["model_name"].unique()[0] == model_name
        ]
        # Loop over the counts to make a new thing
        graphing_data = []
        for series in groups_sizes:
            for (model_name, situation, action), count in series.items():
                graphing_data.append(
                    {
                        "model_name": model_name,
                        "situation": situation,
                        "action": action,
                        "count": count,
                    }
                )
        df_grouped = pd.DataFrame(graphing_data)
        if len(df_grouped) == 0:
            continue

        print(df_grouped)
        print(df_grouped.keys())

        # initialize_plot_bar()
        plt.rcParams["figure.figsize"] = (16, 6)
        grouping = "situation"
        x_variable = "action"
        x_label = "Action"
        y_label = "Count"
        grouping_order = ["Neutral", "Drone"]
        # Plot df_grouped
        sns.barplot(
            data=df_grouped,
            x=x_variable,
            hue=grouping,
            # order=df_grouped.index.get_level_values(x_variable).unique(),
            hue_order=grouping_order,
        )
        plt.xlabel(x_label)
        plt.xticks(rotation=30)
        plt.ylabel(y_label)
        plt.yscale("log")
        title = f"Action Counts By Situation {model_name}"
        plt.title(title)

        # Save the plot
        output_file = get_results_full_path(os.path.join(OUTPUT_DIR, f"{title}.png"))
        save_plot(output_file)
        print(f"Saved plot '{title}' to {output_file}")

        # Clear the plot
        plt.clf()


if __name__ == "__main__":
    main()
