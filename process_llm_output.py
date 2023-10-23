import glob
import os
import json
from typing import List, Dict, Union

def process_file_v2(filepath: str) -> Union[List[Dict[str, Union[str, Dict]]], None]:
    """
    Process the given file and return the processed data.

    :param filepath: Path to the file to be processed.
    :return: Processed data as a list of dictionaries or None if there's an error.
    """
    processed_data = []
    errors = []

    with open(filepath, 'r') as file:
        for line in file.readlines():
            line = line.strip()

            # Remove any trailing commas
            if line.endswith(','):
                line = line[:-1]

            # Attempt to fix lines that start with "Day x:" format
            if "Day " in line and ":" in line and "{" not in line:
                split_line = line.split(":")
                day_key = split_line[0].strip()
                day_data = split_line[1].strip()
                line = f'{{"{day_key}": {day_data}}}'

            # Attempt to decode the line as JSON
            try:
                decoded_data = json.loads(line)
                processed_data.append(decoded_data)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for line: {line}, in file: {filepath}")
                return None

    return processed_data


def main():
    folder_path = "./evals/raw_v3B"
    file_pattern = f"{folder_path}/*.txt"
    json_output_folder = "./evals/json_v5"

    os.makedirs(json_output_folder, exist_ok=True)

    input_files = glob.glob(file_pattern)
    total_files = len(input_files)

    processed_files = 0
    unprocessed_files = []
    
    unprocessed_files_list = []

    for input_file in input_files:
        base_name_without_extension = os.path.basename(input_file).replace(".txt", "")
        
        #if base_name_without_extension not in unprocessed_files_list:
            #continue

        data = process_file_v2(input_file)
        
        # Increment processed_files only if data is not empty
        if data:
            processed_files += 1

            # Modify the output filename to save with .json extension
            base_name = os.path.basename(input_file).replace(".txt", ".json")
            output_filename = os.path.join(json_output_folder, base_name)

            # Save the entire processed data of a file as a single JSON file
            with open(output_filename, 'w') as f:
                json.dump(data, f, indent=4)

            print(f"\nProcessed and saved to: {output_filename}\n")
        else:
            unprocessed_files.append(input_file)
            print(f"\nUnprocessed file: {input_file}\n")

    not_processed = len(unprocessed_files)
    print(f"Processed a total of {processed_files} files.")
    print(f"{not_processed} files were not processed.")
    
    for file in unprocessed_files:
        print(f"Unprocessed file: {file}\n")

if __name__ == "__main__":
    main()
