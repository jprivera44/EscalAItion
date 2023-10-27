"""
Charts for action history.
"""

import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from chart_utils import (
    ALL_SCENARIOS,
    # SCENARIOS_TO_COLORS,
    MODELS_TO_MARKERS,
    MODELS_TO_COLORS,
    # CAPSIZE_DEFAULT,
    ALL_MODEL_NAMES,
    initialize_plot_default,
    # initialize_plot_bar,
    save_plot,
    get_results_full_path,
    # get_color_from_palette,
)

INPUT_DIR = "../evals/json_v5"
OUTPUT_DIR = "./escalation_scores_v2"


def main() -> None:
    """Main function."""

    # Load the data from each file into one big dataframe
    filenames_and_data = [
        (
            filename,
            load_json_data(get_results_full_path(os.path.join(INPUT_DIR, filename))),
        )
        for filename in os.listdir(get_results_full_path(INPUT_DIR))
    ]
    # Create a concatted dataframe using filenames to add columns. Split filenames on spaces, then first element is model_name and second is scenario
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
        if filename.split(" ")[0] in ALL_MODEL_NAMES
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

    # Graph median escalation score simulations for each model together on a lineplot over time
    for scenario in ALL_SCENARIOS:
        df_scenario = pd.concat(dfs_list).query(f"scenario == '{scenario}'")
        # To filter by median, we need to look at all ~5 runs per model, then calculate the sum of the "total" column for each run, then take only the run with the median of that sum
        dfs_to_keep = []
        for model_name in ALL_MODEL_NAMES:
            df_model = df_scenario.query(f"model_name == '{model_name}'")
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
        title = (
            f"Escalation Score Over Time for Median Simulation ({scenario} Scenario)"
        )
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
        del df_plot, dfs_to_keep, title

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


        
        # Calculate day-to-day differences
        df_scenario['daily_difference'] = df_scenario.groupby(['model_name', 'run_index', 'scenario'])['total'].diff().fillna(0)
        # Group by day and calculate mean and standard deviation
        stats_df = df_scenario.groupby(['day','model_name'])['daily_difference'].agg(['mean', 'std']).reset_index()

        #performing error checks on data, ensuring they are numeric and removal of inf values
        stats_df['day'] = pd.to_numeric(stats_df['day'], errors='coerce')
        stats_df['mean'] = pd.to_numeric(stats_df['mean'], errors='coerce')
        stats_df['std'] = pd.to_numeric(stats_df['std'], errors='coerce')
        stats_df.dropna(inplace=True)

        #For loop to plot the difference of mean - std, to show areas of variation
        for model in stats_df['model_name'].unique():
            model_data = stats_df[stats_df['model_name'] == model]
            plt.fill_between(model_data['day'], model_data['mean'] - model_data['std'], model_data['mean'] + model_data['std'], alpha=0.2)


        #Graphing for the 3rd section of difference between days
        grouping = "model_name"
        initialize_plot_default()
        sns.lineplot(
            data=stats_df,
            x="day",
            y="mean",
            hue=grouping,
            palette=MODELS_TO_COLORS,
            hue_order=ALL_MODEL_NAMES,
            dashes=False,
            style=grouping,
            markers=MODELS_TO_MARKERS,
        )
        plt.xlabel("Day")
        plt.ylabel("Avg. Day-to-Day Difference in Escalation Score")
        title = f"Avg. Day-to-Day Difference in Escalation Score Over Time ({scenario})"
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
        del df_scenario, title



def load_json_data(filepath: str) -> pd.DataFrame:
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
