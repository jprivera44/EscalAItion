import pandas as pd

def save_file_by_color(df, color):
    """
    Save rows of the dataframe to a CSV file based on the specified color.

    Args:
    df (DataFrame): The original dataframe.
    color (str): The color to filter by.
    """
    df_color = df[df['self'] == color]
    # Replace 'your_file.csv' with the path to your CSV file

    df_color.to_csv(f'{color}.csv', index=False)

def main():
    #set variables to save the file
    file_save_locaion = 'results/actions_by_color/'

    #create the file read location
    file_read_location = 'results/actions_v4/'


    # Read the original CSV file
    # Replace 'your_file.csv' with the path to your CSV file
    df = pd.read_csv(file_read_location + '*.csv')

    # Identify the unique colors in the 'self' column
    unique_colors = df['self'].unique()

    # For each unique color, save the filtered data to a new CSV file
    for color in unique_colors:
        save_file_by_color(df, color)

if __name__ == "__main__":
    main()
