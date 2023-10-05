import glob
import os
import json
from typing import List, Dict, Union

def process_file_v2(filename: str) -> List[Dict[str, Union[str, int]]]:
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    data = []
    for line in lines:
        try:
            json_data = json.loads(line.strip())
            data.append(json_data)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for line: {line.strip()}, in file: {filename}")
            
    return data

def main():
    folder_path = "./evals/raw_v2"
    file_pattern = f"{folder_path}/GPT-4 D*.txt"
    json_output_folder = "./evals/json_v2"

    
    os.makedirs(json_output_folder, exist_ok=True)

    input_files = glob.glob(file_pattern)
    
    processed_files = 0
    for input_file in input_files:
        data = process_file_v2(input_file)
        
       # Modify the output filename to save with .json extension
        base_name = os.path.basename(input_file).replace(".txt", ".json")
        output_filename = os.path.join(json_output_folder, base_name)
        
        # Save the entire processed data of a file as a single JSON file
        with open(output_filename, 'w') as f:
            json.dump(data, f, indent=4)
        
        processed_files += 1
        print(f"Processed and saved to: {output_filename}")
    
    print(f"Processed a total of {processed_files} files.")

if __name__ == "__main__":
    main()
