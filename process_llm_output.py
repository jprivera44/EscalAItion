

import re
import json
import os
import glob

import hashlib
import os
import glob


def process_txt_to_json(input_txt_path, output_json_path):
    # Read the content from the provided txt file
    with open(input_txt_path, "r") as file:
        raw_content = file.read()

    # Remove newline characters using regex
    adjusted_content_no_newlines = re.sub(r'\\n', '', raw_content)

    # Adjust the content to replace the single quotes enclosing the `completion` value with double quotes
    adjusted_content_double_quotes = adjusted_content_no_newlines.replace("completion='", '"completion": "').replace("',", '",')
    adjusted_content_double_quotes = adjusted_content_double_quotes.replace('\'', '"')

    # Wrap the content in curly braces
    wrapped_content = '{' + adjusted_content_double_quotes + '}'

    # Adjust the content to remove the leading and trailing double quotes from the "completion" value
    adjusted_content_no_quotes = wrapped_content.replace('"completion": "{', '"completion": {').replace('}",', '},')

    # Adjust the content to enclose specific keys in double quotes
    adjusted_content_quoted_keys = adjusted_content_no_quotes.replace("completion_time_sec=", '"completion_time_sec":')
    adjusted_content_quoted_keys = adjusted_content_quoted_keys.replace(", prompt_tokens=", ', "prompt_tokens":')
    adjusted_content_quoted_keys = adjusted_content_quoted_keys.replace(", completion_tokens=", ', "completion_tokens":')
    adjusted_content_quoted_keys = adjusted_content_quoted_keys.replace(", total_tokens=", ', "total_tokens":')

    # Further adjustments to ensure all keys are enclosed in double quotes
    final_adjusted_content = adjusted_content_quoted_keys.replace("completion_time_sec:", '"completion_time_sec":')
    final_adjusted_content = final_adjusted_content.replace("prompt_tokens:", '"prompt_tokens":')
    final_adjusted_content = final_adjusted_content.replace("completion_tokens:", '"completion_tokens":')
    final_adjusted_content = final_adjusted_content.replace("total_tokens:", '"total_tokens":')

    #if the parsing of the final JSON fails, print a debug message and the file name, then continue, along with total count of files not parsed
    try:
    # Parse the final adjusted content as JSON
        content_dict = json.loads(final_adjusted_content)
        print(f"DEBUG: File '{input_txt_path}' WORKING")
    except:
        print(f"DEBUG: File '{input_txt_path}' BROKEN")
        return None

    # Assertions to ensure the content structure matches expectation
    assert "completion_time_sec" in content_dict, "Key 'completion_time_sec' not found"
    assert "prompt_tokens" in content_dict, "Key 'prompt_tokens' not found"
    assert "completion_tokens" in content_dict, "Key 'completion_tokens' not found"
    assert "total_tokens" in content_dict, "Key 'total_tokens' not found"

    # Assert that 'completion' is a dictionary and contains keys named like 'Day X'
    assert isinstance(content_dict["completion"], dict), "'completion' is not a dictionary"
    day_keys = [f"Day {i}" for i in range(1, 15)]
    for day_key in day_keys:
        assert day_key in content_dict["completion"], f"Key '{day_key}' not found in 'completion'"
    
    #check if the completion tokens are above 500 tokens if not print a debug message and the file name
    if content_dict["completion_tokens"] < 500:
        print(f"DEBUG: File '{input_txt_path}' has completion_tokens below 500. Value: {content_dict['completion_tokens']}")

    # Save the processed content to the specified output JSON file
    #with open(output_json_path, "w") as file:
     #   json.dump(content_dict, file, indent=4)

    return output_json_path

# Example usage:
# output_path = process_txt_to_json("input.txt", "output.json")


def structural_hash(file_content):
    """Generate a hash based on the structural elements of the file's content."""
    # Remove numbers and non-structural text (retain only structural elements like braces, quotes, colons, commas, etc.)
    structural_content = ''.join(char if char in '{}[]":,' else 'X' for char in file_content)
    return hashlib.md5(structural_content.encode()).hexdigest()

def compare_file_structures(directory_path):
    """Compare files in a directory based on their structural hash."""
    structure_hashes = {}
    
    # Get all files in the directory
    files = glob.glob(os.path.join(directory_path, "*.txt"))
    
    for file in files:
        with open(file, 'r') as f:
            content = f.read()
        file_structure_hash = structural_hash(content)
        if file_structure_hash in structure_hashes:
            structure_hashes[file_structure_hash].append(file)
        else:
            structure_hashes[file_structure_hash] = [file]
    
    return structure_hashes







def main():
    #call the function above on all files in the folder
    folder_path = "./evals/raw"
    file_pattern = f"{folder_path}/*.txt"
    json_output_folder = "./evals/json/gpt3-5"

    os.makedirs(json_output_folder, exist_ok=True)


    #testing file structure
    # Testing the function on the sample directory
    
    structure_groups = compare_file_structures(folder_path)
    print(structure_groups)


    '''
    # Use glob to get a list of file paths that match the pattern
    file_paths = glob.glob(file_pattern)

    for file in file_paths:
        base_name = os.path.basename(file)
        file_name_without_extension = os.path.splitext(base_name)[0]
        print("Processing file:", file_name_without_extension)

        output_path = process_txt_to_json(file, f"{json_output_folder}/{file_name_without_extension}.json")
    '''


if __name__ == "__main__":
    main()
