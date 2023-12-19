import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_json_data(filepath: str) -> pd.DataFrame:
    """Load the JSON of an escalation eval into a dataframe with [day, total] columns."""
    with open(filepath, encoding="utf-8") as file:
        json_data = json.load(file)
    data_rows = []
    for input_row in json_data:
        day = input_row["Day"]
        total = int(input_row["Total"])
        data_rows.append({"day": day, "total": total})
    return pd.DataFrame(data_rows)

def main():
    INPUT_DIR = "./evals/prompt_ablations_total_all_files"  # Directory containing your JSON files
    OUTPUT_DIR = "./output_ablations/"  # Directory where the plot will be saved

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Load and aggregate data
    all_data = []
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".json"):
            model, experiment, _ = filename.split("_", 2)
            df = load_json_data(os.path.join(INPUT_DIR, filename))
            df["model"] = model
            df["experiment"] = experiment
            all_data.append(df)
    
    full_data = pd.concat(all_data)

    # Unique models and experiments
    unique_models = full_data['model'].unique()
    unique_experiments = full_data['experiment'].unique()

    # Create subplots
    fig, axes = plt.subplots(len(unique_experiments), len(unique_models), figsize=(15, 5 * len(unique_experiments)))

    # Setting the colors (update or expand as needed)
    model_colors = {
        "gpt-3.5": "green",
        "gpt-4": "purple",
        "claude-2.0": "blue"
    }

    for i, experiment in enumerate(unique_experiments):
        for j, model in enumerate(unique_models):
            ax = axes[i, j] if len(unique_experiments) > 1 else axes[j]
            df_filtered = full_data[(full_data['experiment'] == experiment) & (full_data['model'] == model)]
            sns.lineplot(ax=ax, x='day', y='total', data=df_filtered, color=model_colors.get(model, "black"))
            ax.set_title(f"{model} - {experiment}")
            ax.set_xlabel("Day")
            ax.set_ylabel("Total Escalation")

    plt.suptitle("Escalation Scores Over Time by Model and Experiment")
    plt.tight_layout()

    # Save the plot
    output_filepath = os.path.join(OUTPUT_DIR, "escalation_scores_plot.png")
    plt.savefig(output_filepath)
    plt.close()

if __name__ == "__main__":
    main()
