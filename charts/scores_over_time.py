"""
Charts for scores over time
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from chart_utils import (
    initialize_plot_default,
    save_plot,
    get_results_full_path,
)

INPUT_DIR = "../results/default"
OUTPUT_DIR = "./scores_over_time"

ACTIONS_SUBDIR = "actions"


def main() -> None:
    """Main function."""

    # Load the data from each file into one big dataframe
    df_all = pd.concat(
        [
            pd.read_csv(get_results_full_path(os.path.join(INPUT_DIR, f)))
            for f in os.listdir(get_results_full_path(INPUT_DIR))
        ]
    )

    # Rename the agent_model to display names
    df_all["agent_model"] = df_all["agent_model"].apply(
        lambda x: MODEL_NAME_TO_DISPLAY_NAME[x].replace("\n", " ")
    )

    # Sort according to MODEL_ORDER
    df_all["agent_model"] = pd.Categorical(
        df_all["agent_model"], categories=MODEL_ORDER_NO_NEWLINES, ordered=True
    )
    df_all.sort_values("agent_model", inplace=True)

    # Print how many runs there are for each agent_model combo
    print("Runs per agent_model, year_integer combo:")
    print(df_all.groupby(["agent_model"]).size())

    # Plot a bunch of different bar graphs for different metrics
    for metric_prefix, y_label, improvement_sign in [
        ("score/units", "Average Unit Count", 0),
        ("score/centers", "Average Number of Supply Centers", 1),
        ("score/welfare", "Average Welfare Points", 1),
    ]:
        # Initialize
        initialize_plot_default()

        # Bigger figure since it's busy
        plt.rcParams["figure.figsize"] = (10, 5)

        # Plot the welfare scores for each power
        cols_of_interest = [
            "agent_model",
            "year_integer",
        ] + [f"{metric_prefix}/{power}" for power in ALL_POWER_ABBREVIATIONS]

        plot_df = df_all[cols_of_interest].copy()

        # Average together all the columns starting with metric_prefix
        metric_columns = [
            col for col in plot_df.columns if col.startswith(metric_prefix)
        ]
        plot_df[y_label] = plot_df[metric_columns].mean(axis=1)
        plot_df.drop(columns=metric_columns, inplace=True)

        # update the column names
        grouping = "agent_model"
        x_label = "Years Elapsed"
        plot_df.columns = [grouping, x_label, y_label]

        # Create the plot
        sns.lineplot(
            data=plot_df,
            x=x_label,
            y=y_label,
            hue=grouping,
            palette=MODEL_NAME_TO_COLOR,
            style=grouping,
            markers=True,
            dashes=False,
            errorbar="ci",
        )

        # Set labels and title
        plt.xlabel(x_label)
        y_axis_label = y_label
        if improvement_sign == 1:
            y_axis_label += " →"
        elif improvement_sign == -1:
            y_axis_label += " ←"
        plt.ylabel(y_axis_label)
        title = f"{y_label} Across Years by Model (Self-Play)"
        plt.title(title)

        # # Legend in 2 columns
        # plt.legend(
        #     borderaxespad=0.0,
        #     ncol=2,
        #     handletextpad=0.1,
        #     columnspacing=0.5,
        #     framealpha=0.25,
        # )

        # Legend to the right of the plot
        plt.legend(
            borderaxespad=0.0,
            bbox_to_anchor=(1.01, 1),
            loc="upper left",
            handletextpad=0.1,
            # columnspacing=1,
            labelspacing=1.5,
            # Order by
            # framealpha=0.25,
        )

        # Save the plot
        output_file = get_results_full_path(
            os.path.join(OUTPUT_DIR, f"Scores {y_label}.png")
        )
        save_plot(output_file)
        print(f"Saved plot '{title}' to {output_file}")

        # Clear the plot
        plt.clf()


if __name__ == "__main__":
    main()
