import pandas as pd
import os
import glob

def save_file_by_color(df, color, original_filename, file_save_location):
    """
    Save rows of the dataframe to a CSV file based on the specified color and original filename.

    Args:
    df (DataFrame): The original dataframe.
    color (str): The color to filter by.
    original_filename (str): The name of the original file.
    file_save_location (str): The location to save the output files.
    """
    df_color = df[df['self'] == color]
    # Construct the new filename
    new_filename = f'{file_save_location}{original_filename}_{color}.csv'
    df_color.to_csv(new_filename, index=False)

def main():
    # Set variables for file save and read locations
    file_save_location = 'results/actions_by_color_v3/'
    file_read_location = 'results/actions_v3/'

    #if filename save location does not exist, create it
    if not os.path.exists(file_save_location):
        os.makedirs(file_save_location)

    # Create a pattern for all CSV files in the read directory
    file_pattern = os.path.join(file_read_location, '*.csv')

    # Iterate over each CSV file in the directory
    for filepath in glob.glob(file_pattern):
        # Extract the original filename without extension
        original_filename = os.path.basename(filepath).replace('.csv', '')

        # Read the CSV file
        df = pd.read_csv(filepath)

        # Identify the unique colors in the 'self' column
        unique_colors = df['self'].unique()

        # For each unique color, save the filtered data to a new CSV file
        for color in unique_colors:
            save_file_by_color(df, color, original_filename, file_save_location)
        

if __name__ == "__main__":
    main()
