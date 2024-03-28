import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

from chart_utils import (
    save_plot,
    initialize_plot_bar,
    ALL_MODEL_NAMES,
    ABLATION_NAME_ORDER_NEWLINES,
    ABLATION_PATTERNS_TO_PRETTY_NAMES,
    CAPSIZE_DEFAULT,
    MODELS_TO_COLORS,
)


def transform_model_name(model_name):
    if 'gpt' in model_name.lower():
        return model_name.upper()  # Convert 'gpt' models to uppercase
    elif 'claude' in model_name.lower():
        return model_name.capitalize()  # Capitalize 'claude' models
    else:
        return model_name

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



import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import matplotlib.ticker as ticker

# ... [rest of your imports and definitions] ...

def plot_subset(experiments, suffix, unique_models, model_colors, full_data, OUTPUT_DIR):
    print("in the plot subset function")
    # Increase the vertical space if needed
    fig, axes = plt.subplots(len(experiments), len(unique_models), figsize=(20, 6 * len(experiments)), sharex=True, sharey=True)

    if len(experiments) == 1:
        axes = [axes]  # Wrap it in a list to make the indexing below work
    elif len(unique_models) == 1:
        axes = axes.reshape(-1, 1)  # If only one model, ensure axes are 2D array

    for i, experiment in enumerate(experiments):
        for j, model in enumerate(unique_models):
            ax = axes[i][j] if axes.ndim > 1 else axes[i]
            df_filtered = full_data[(full_data['experiment'] == experiment) & (full_data['model'] == model)]
            line = sns.lineplot(ax=ax, x='day', y='total', data=df_filtered, color=model_colors[model], label=f"{model} - {experiment}")
            
            df_average = df_filtered.groupby('day')['total'].mean().reset_index()
            sns.scatterplot(ax=ax, x='day', y='total', data=df_average, color=model_colors[model], s=50, zorder=10)

            ax.set_ylabel("Escalation Score", fontsize=16)
            ax.grid(True)
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=6))
            ax.set_xlabel("Time t [Days]", fontsize=14)

            # Reduce the font size if the legend is still too large
            ax.legend(loc='upper left', fontsize=15)

    plt.suptitle(f"Escalation Scores Over Time by Model and Experiment ({suffix})", fontsize=28)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_filepath = os.path.join(OUTPUT_DIR, f"escalation_scores_plot_{suffix}.pdf")
    plt.savefig(output_filepath, bbox_inches='tight')  # Save with tight bounding box to include legend
    plt.show()  # Display the figure

# ... [rest of your code] ...






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

     #Function to plot a subset of experiments
    

    my_ablations_mapping = {
    'Neutral': 'Original',
    'NoMessage': 'No Messaging',
    'noHistory': 'No History', # Assuming 'noHistory' is the correct form in your data
    'NoPastActions': 'No Past Actions',
    'shutdown': 'Shutdown When Nuked', # Assuming 'shutdown' is the correct form in your data
    'noGoals': 'No Goals', # Assuming 'noGoals' is the correct form in your data
    'freedom': 'Action Autonomy', # Assuming 'freedom' is the correct form in your data
    'simulation': 'Low-Stakes Simulation' # Assuming 'simulation' is the correct form in your data
    }

    experiment_order = [
    'Original',
    'No Messaging',
    'No History',
    'No Past Actions',
    'Shutdown When Nuked',
    'No Goals',
    'Action Autonomy',
    'Low-Stakes Simulation'
]

    # Replace the experiment names in the DataFrame
    full_data['experiment'] = full_data['experiment'].replace(my_ablations_mapping)
    full_data['model'] = full_data['model'].apply(transform_model_name)

    

    # Unique models and experiments
    unique_models = full_data['model'].unique()
    unique_experiments = full_data['experiment'].unique()
    print("unique_experiments", unique_experiments)
    print("ablation patters", ABLATION_PATTERNS_TO_PRETTY_NAMES)

    print("unique_models", unique_models)
    print("full_data unique models", full_data['model'].unique())

    # Create subplots
    fig, axes = plt.subplots(len(unique_experiments), len(unique_models), figsize=(15, 5 * len(unique_experiments)), sharex=True, sharey=True)

    # Setting the colors (update or expand as needed)
    model_colors = {
        "GPT-3.5": "green",
        "GPT-4": "purple",
        "Claude-2.0": "blue"
    }


    # Divide the experiments into two parts
    first_half_experiment_order = experiment_order[:4]  # First four experiments
    second_half_experiment_order = experiment_order[4:]  # Last four experiments

    print("main first half", first_half_experiment_order)

    # Plot and save the first subset
    plot_subset(first_half_experiment_order, 'first_half', unique_models,model_colors, full_data, OUTPUT_DIR)

    
    # Plot and save the second subset
    plot_subset(second_half_experiment_order, 'second_half', unique_models,model_colors, full_data, OUTPUT_DIR)





    # Iterate over each experiment and model to create subplots
    for i, experiment in enumerate(experiment_order):
        for j, model in enumerate(unique_models):
            ax = axes[i][j] if len(unique_experiments) > 1 else axes[j]
            df_filtered = full_data[(full_data['experiment'] == experiment) & (full_data['model'] == model)]
            sns.lineplot(ax=ax, x='day', y='total', data=df_filtered, color=model_colors[model])
            
            df_average = df_filtered.groupby('day')['total'].mean().reset_index()
            sns.scatterplot(ax=ax, x='day', y='total', data=df_average, color=model_colors[model], s=50, zorder=10)
        

            ax.set_ylabel("Escalation Score", fontsize=2)
            ax.grid(True)
            
            # Set x-ticks for all subplots. Here we use MaxNLocator to ensure a fixed number of ticks
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=6))  # Ensures integer ticks with a maximum of 6 bins


            # Only set x-label for bottom row subplots
            #if i == len(unique_experiments) - 1:
            ax.set_xlabel("Time t [Days]")
            
            # Create a legend for the current subplot that includes the model and the scenario
            legend_label = f'{model} - {experiment}'  # Combining model and scenario into one label
            ax.legend([ax.lines[0]], [legend_label], loc='upper left')

    plt.suptitle("Escalation Scores Over Time by Model and Experiment")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust the rect if the suptitle overlaps with the top subplot

    # Save the plot
    output_filepath = os.path.join(OUTPUT_DIR, "escalation_scores_plot.pdf")
    plt.savefig(output_filepath)
    plt.close()
    plt.show()

if __name__ == "__main__":
    main()


