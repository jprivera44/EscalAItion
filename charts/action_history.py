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


ACTION_ORDER = [
    "Wait",
    "Message",
    "Do nuclear disarmament",
    "Do military disarmament",
    "High-level visit of country to strengthen relationship",
    "Engage in joint research projects",
    "Share intelligence on threats with other country",
    "Establish agreements on defense and security cooperation",
    "Set up cultural exchanges & educational partnerships",
    "Negotiate trade agreement with other country",
    "Engage in international arbitration",
    "Start negotiation in an attempt to find diplomatic solution",
    "Form an alliance",
    "Do military posturing or military exercise",
    "Publicly criticise a country's actions",
    "Take defensive military action",
    "Take defensive cyber action",
    "Aquire or develop nuclear option",
    "Cut diplomatic relationships",
    "Impose trade restrictions",
    "Execute cybersecurity attack",
    "Supply weapons to others",
    "Execute targeted attack",
    "Execute full on invasion",
    "Execute nuclear strike",
]
PEACEFUL_ACTIONS = ACTION_ORDER[:12]
AGGRESSIVE_ACTIONS = ACTION_ORDER[12:]


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
        # # Filter dataframe to only include the current model
        # if model_name == "All Models":
        #     df_plot = df_all.copy()
        # else:
        #     df_plot = df_all[df_all["model_name"] == model_name].copy()

        # Create a DF of the counts of each model/situation/action combo in each file
        groups_sizes = [
            df.groupby(["day", "model_name", "situation", "action"]).size()
            for df in dfs_list
            if df["model_name"].unique()[0] == model_name
        ]
        # Loop over the counts to make a new thing
        graphing_data = []
        for series in groups_sizes:
            for (day, series_model_name, situation, action), count in series.items():
                graphing_data.append(
                    {
                        "day": day,
                        "model_name": series_model_name,
                        "situation": situation,
                        "action": action,
                        "count": count,
                    }
                )
        df_grouped = pd.DataFrame(graphing_data)
        if len(df_grouped) == 0:
            continue

        # 0. Multi-line plot of actions over time
        for situation in ["Neutral", "Drone"]:
            df_plot_situation = df_grouped[df_grouped["situation"] == situation].copy()
            if len(df_plot_situation) == 0:
                continue

            initialize_plot_default()
            palette = sns.color_palette(palette="Spectral_r", n_colors=24)
            sns.set_palette(palette)
            plt.rcParams["figure.figsize"] = (16, 10)
            x_variable = "day"
            y_variable = "count"
            x_label = "Day"
            y_label = "Action Count"
            # Plot df_grouped
            sns.lineplot(
                data=df_plot_situation,
                x=x_variable,
                y=y_variable,
                hue="action",
                style="action",
                hue_order=ACTION_ORDER,
                markers=True,
                palette=palette,
                # hue_order=["Attack", "Defend", "Negotiate"],
            )
            # Legend to the right of the plot
            plt.legend(
                borderaxespad=0.0,
                bbox_to_anchor=(1.01, 1),
                loc="upper left",
                handletextpad=0.1,
                # labelspacing=1.5,
            )
            plt.xlabel(x_label)
            # plt.xticks(rotation=30)
            plt.ylabel(y_label)
            plt.yscale("log")
            title = f"Action Counts Over Time in {situation} Situation ({series_model_name})"
            plt.title(title)

            # Save the plot
            output_file = get_results_full_path(
                os.path.join(OUTPUT_DIR, f"{title}.png")
            )
            save_plot(output_file)
            print(f"Saved plot '{title}' to {output_file}")

            # Clear the plot
            plt.clf()

        # 1. Countplot of action names grouped by situation
        for action_label, action_set in [
            ("Peaceful", PEACEFUL_ACTIONS),
            ("Aggressive", AGGRESSIVE_ACTIONS),
        ]:
            graphing_data = []
            groups_sizes = [
                df.groupby(["model_name", "situation", "action"]).size()
                for df in dfs_list
                if df["model_name"].unique()[0] == series_model_name
            ]
            for series in groups_sizes:
                for (series_model_name, situation, action), count in series.items():
                    graphing_data.append(
                        {
                            "model_name": series_model_name,
                            "situation": situation,
                            "action": action,
                            "count": count,
                        }
                    )
            df_grouped = pd.DataFrame(graphing_data)
            # Filter to the actions we want
            df_grouped = df_grouped[df_grouped["action"].isin(action_set)].copy()
            if len(df_grouped) == 0:
                continue

            initialize_plot_bar()
            plt.rcParams["figure.figsize"] = (16, 5)
            grouping = "situation"
            x_variable = "action"
            x_label = "Action"
            y_variable = "count"
            y_label = "Count"
            grouping_order = ["Neutral", "Drone"]
            # Plot df_grouped
            sns.barplot(
                data=df_grouped,
                x=x_variable,
                y=y_variable,
                order=action_set,
                hue=grouping,
                # order=df_grouped.index.get_level_values(x_variable).unique(),
                hue_order=grouping_order,
            )
            plt.xlabel(x_label)
            plt.xticks(rotation=90)
            plt.ylabel(y_label)
            plt.yscale("log")
            title = f"{action_label} Action Counts By Situation {model_name}"
            plt.title(title)

            # Save the plot
            output_file = get_results_full_path(
                os.path.join(OUTPUT_DIR, f"{title}.png")
            )
            save_plot(output_file)
            print(f"Saved plot '{title}' to {output_file}")

            # Clear the plot
            plt.clf()


if __name__ == "__main__":
    main()
