"""
Effect of prompt ablations on dynamic variables.
"""

import os

import matplotlib.pyplot as plt

# import numpy as np
import pandas as pd
import seaborn as sns

from chart_utils import (
    ABLATION_NAME_ORDER,
    ABLATION_PATTERNS_TO_PRETTY_NAMES,
    ALL_DYNAMIC_VARIABLES,
    DYNAMIC_VARIABLES_TO_NAMES,
    LABELSIZE_DEFAULT,
    TIMELABEL_DEFAULT,
    initialize_plot_default,
    save_plot,
    get_results_full_path,
)

SCENARIO = "NEUTRAL"

OUTPUT_DIR = "./ablations_dynamic_variables"

PLOT_NUMBER_TO_CREATE = 1

LABEL_MAX_LENGTH = 26


def filename_to_pretty_ablation_name(filename: str) -> str:
    """Format downloaded filenames into graphable names."""

    for pattern, pretty_name in ABLATION_PATTERNS_TO_PRETTY_NAMES.items():
        if pattern in filename:
            return pretty_name
    raise ValueError(f"Could not find a pretty name for filename {filename}")


def main() -> None:
    """Main function."""

    for model_name in ["GPT-3.5", "GPT-4", "Claude-2.0"]:
        # Load the data from each file into one big dataframe
        input_dir = f"../results/prompt_ablations/{model_name.lower()}/variables_v1"
        filenames_and_data = [
            (
                filename,
                pd.read_csv(get_results_full_path(os.path.join(input_dir, filename))),
            )
            for filename in os.listdir(get_results_full_path(input_dir))
        ]
        # Create a concatted dataframe using filenames to add columns. Split filenames on spaces, then first element is model_name and second is scenario
        dfs_list_unprocessed = [
            df.assign(
                ablation=filename_to_pretty_ablation_name(filename),
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
        df_all = pd.concat(dfs_list)

        # Print how many runs there are for each ablation
        print("Runs per ablation combo:")
        print(df_all.groupby(["ablation"], observed=True).size())

        if PLOT_NUMBER_TO_CREATE == 1:
            # Dynamic vars over time with lines for different ablations
            for dynamic_variable in ALL_DYNAMIC_VARIABLES:
                plot_dynamic_variables(df_all, model_name, dynamic_variable)


def plot_dynamic_variables(df_all, model_name, dynamic_variable):
    """Plot line graphs of the dynamic variable for each ablation group."""
    if len(df_all) == 0:
        print(f"⚠️ Warning: No data for {model_name} and {dynamic_variable} variable")
        return
    assert (
        "_dynamic" in dynamic_variable
    ), f"dynamic variable={dynamic_variable} (expected to contain '_dynamic')"

    initialize_plot_default()
    plt.figure(figsize=(7.5, 6.25))
    x_variable = "day"
    x_label = TIMELABEL_DEFAULT
    y_variable = dynamic_variable.split("_dynamic")[0].replace("_", " ")
    y_label = DYNAMIC_VARIABLES_TO_NAMES[dynamic_variable]
    grouping = "ablation"
    grouping_order = ABLATION_NAME_ORDER
    palette = ["#444"] + sns.color_palette(None, len(grouping_order) - 1)
    # Plot df_grouped
    sns.lineplot(
        data=df_all,
        x=x_variable,
        y=y_variable,
        hue=grouping,
        style=grouping,
        hue_order=grouping_order,
        # errorbar=("se", 1),
        errorbar="se",
        # n_boot=5000,
        # seed=10,
        # errorbar=None,
        palette=palette,
        dashes=False,
        markers=True,
    )
    plt.xlabel(x_label, size=LABELSIZE_DEFAULT)
    plt.ylabel(y_label, size=LABELSIZE_DEFAULT)
    title = f"{y_label} ({model_name})"
    plt.title(title)

    loc = (
        "lower left"
        if dynamic_variable == "population_dynamic"
        else "best"
        if dynamic_variable == "nuclear_dynamic"
        else "upper left"
    )
    plt.legend(
        # bbox_to_anchor=(1.05, 1),
        loc=loc,
        borderaxespad=0.0,
        # ncol=2,
        title="Prompt Variation",
        handletextpad=0.1,
        labelspacing=0.25,
        # framealpha=0.5,
        columnspacing=0.25,
    )
    if dynamic_variable == "nuclear_dynamic" and model_name != "Claude-2.0":
        # Remove legend, just doesn't fit well
        plt.legend().remove()

    # Save the plot
    save_plot(
        OUTPUT_DIR,
        f"ablate_var_{DYNAMIC_VARIABLES_TO_NAMES[dynamic_variable]}_{model_name}",
    )

    # Clear the plot
    plt.clf()
    plt.close()


if __name__ == "__main__":
    main()
