import json
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def flatten_data(data):
    """
    Flattens the nested 'Frameworks' key in the data.
    """
    flattened = []
    for item in data:
        new_item = item.copy()  # Make a copy to avoid modifying the original data
        frameworks = new_item.pop('Frameworks', {})
        for key, value in frameworks.items():
            new_item[key] = value
        flattened.append(new_item)
    return flattened


def initialize_plot_default():
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (12, 8)


def make_spectral_chart(data, action_type, group_name):
    unique_filenames = set([item["filename"] for item in data])
    print(f"Unique filenames: {unique_filenames}")
    print(f"Number of unique filenames: {len(unique_filenames)}")

    # Initialize the plot
    initialize_plot_default()

    n_colors = len(unique_filenames)

    palette = sns.color_palette(palette="Spectral_r", n_colors=n_colors)
    print(f"Palette size: {len(palette)}")
    sns.set_palette(palette)

    df = pd.DataFrame(data)

    # Spectral chart plotting
    ax = sns.lineplot(
        data=df,
        x="Day",
        y=action_type,
        hue="filename",
        markers=True,
        dashes=False,   # Ensures a solid line
        lw=2,           # Line width
        palette=palette
    )

    # Adding shading under the line
    for line in ax.lines:
        x, y = line.get_data()
        ax.fill_between(x, y1=y, y2=0, alpha=0.3)

    # Styling
    plt.legend(
        borderaxespad=0.0,
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
        handletextpad=0.1,
    )
    plt.xlabel("Day")
    plt.ylabel(action_type)
    title = f"{action_type} Over Time for {group_name}"
    plt.title(title)
    plt.show()

    # Save the plot
    output_filename = f"./output/{title}.png"
    #plt.savefig(output_filename)
    print(f"Saved plot '{title}' to {output_filename}")

    # Clear the plot for the next graph
    plt.clf()



def main():
    file_patterns = [
        "./evals/json_v2/GPT-4 D*.json",
        # Add more file patterns here
    ]

    all_data = {}

    for pattern in file_patterns:
        input_files = glob.glob(pattern)

        for file in input_files:
            with open(file, 'r') as f:
                data = json.load(f)
            
            data = flatten_data(data)  # <-- Flatten the data here

            # Extracting the prefix (like GPT-4 Drone) to group files by type
            prefix = os.path.basename(file).rsplit(' ', 2)[0]

            if prefix not in all_data:
                all_data[prefix] = []

            # Attach filename to each data point to use as hue in the graph
            for point in data:
                point["filename"] = os.path.basename(file)

            all_data[prefix].extend(data)

    # Graph Types
    action_metrics = [
        "Just Cause & Authority",
        "Intention & Success",
        "Last Resort & Proportionality",
        "UN Charter & R2P",
        "Severity",
        "Retaliation",
        "Public vs Private",
        "Risky Actions",
        "Total"
    ]

    # Create spectral charts for each metric and each group of files
    for group_name, data in all_data.items():
        for metric in action_metrics:
            make_spectral_chart(data, metric, group_name)


if __name__ == "__main__":
    main()
