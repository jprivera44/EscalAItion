import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import json

from chart_utils import (
    save_plot,
    ALL_MODEL_NAMES,
    MODELS_TO_COLORS,
)

def extract_model_scenario(filename):
    """Extract the model and scenario from the filename."""
    parts = filename.split('_')
    model = parts[0]
    scenario = parts[1].replace(".json", "")
    return model, scenario

def read_json_file(filepath):
    """Read JSON data from a file."""
    with open(filepath, 'r') as file:
        return json.load(file)

# Assuming all files are in a directory named 'data'
directory = 'evals/prompt_ablations_total_all_files_v2'
OUTPUT_DIR = 'ablations_bar_charts/'
title = 'prompt_ablations_all'


# Initialize a list to store data from all files
all_data = []

# Iterate over each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        data = read_json_file(filepath)
        
        # Extract model and scenario
        model, scenario = extract_model_scenario(filename)

        # Add model and scenario information to each row
        for row in data:
            row['Model'] = model
            row['Scenario'] = scenario
            all_data.append(row)

# Convert all data into a DataFrame
combined_df = pd.DataFrame(all_data)


# Display the DataFrame
print(combined_df)

# Group by Model and Scenario and calculate the average of 'Total'
average_totals = combined_df.groupby(['Model', 'Scenario'])['Total'].mean().reset_index()

# For 'gpt' models, capitalize the entire model name
average_totals.loc[average_totals['Model'].str.contains('gpt'), 'Model'] = \
    average_totals.loc[average_totals['Model'].str.contains('gpt'), 'Model'].str.upper()

# For 'claude' models, capitalize only the first letter of the model name
average_totals.loc[average_totals['Model'].str.contains('claude'), 'Model'] = \
    average_totals.loc[average_totals['Model'].str.contains('claude'), 'Model'].str.capitalize()


# Rename the columns for clarity
average_totals.columns = ['Model', 'Scenario', 'Average Total']



# Display the resulting DataFrame
print(average_totals)

# Pivot the DataFrame to have scenarios as columns, models as rows
pivot_df = average_totals.pivot(index='Model', columns='Scenario', values='Average Total')

# Find the maximum value for setting the same y-axis scale
max_value = pivot_df.max().max()




# Set the style
sns.set(style="whitegrid")

# Create a color palette
palette = sns.color_palette("pastel")

# Create the bar chart
plt.figure(figsize=(14, 8))
barplot = sns.barplot(
    x='Scenario', 
    y='Average Total', 
    hue='Model', 
    data=average_totals, 
    palette=MODELS_TO_COLORS,
    hue_order=ALL_MODEL_NAMES
)

# Improve readability by adjusting the following:
plt.title('Average Escalation Score per Model and Scenario', fontsize=16)
plt.xlabel('Scenario', fontsize=14)
plt.ylabel('Average Total', fontsize=14)
plt.xticks(fontsize=12, rotation=45)
plt.yticks(fontsize=12)
plt.legend(title='Model', fontsize=12)
save_plot(OUTPUT_DIR, title)

# Set the background grid
plt.grid(True, linestyle='--', linewidth=0.6, color='grey')
barplot.set_axisbelow(True)

# Show plot
plt.tight_layout()
plt.show()
