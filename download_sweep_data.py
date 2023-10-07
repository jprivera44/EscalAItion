"""Download artifacts from runs in a sweep for later analysis."""

import os
import json

import pandas as pd
from tqdm import tqdm
import wandb

import constants

OUTPUT_FOLDER_ACTIONS = "results/actions_v2"
OUTPUT_FOLDER_VARIABLES = "results/variables_v2"


def main():
    r"""
    Main function to download the data.

    Note: From a sweeps page, you can run the following JavaScript console command to print the IDs and names of the runs in CSV format:
    ```
    output = "sweep_id,prefix\n"
    labels = document.querySelectorAll('a > span > .editable-label')
    for (let i = 0; i < labels.length; i++) {
        label = labels[i]
        sweep_id = label.parentElement.parentElement.href.split("/")[6]
        output += sweep_id + "," + label.innerHTML + "\n"
    }
    console.log(output)
    ```
    You may then want to modify it to remove bad sweeps or have different prefixes (e.g. without version numbers).
    """

    # Get user input for the sweep ID
    sweep_id_and_maybe_prefix = input(
        "Enter either:\n\t1. The sweep ID\n\t2. The sweep ID and optionally a space then the prefix for donloaded files\n\t3. A path to a CSV text file with 'sweep_id' and 'prefix' columns\n"
    )
    if sweep_id_and_maybe_prefix.endswith(".csv"):
        df = pd.read_csv(sweep_id_and_maybe_prefix)
        for _, row in tqdm(df.iterrows(), total=len(df), desc="🧹 Sweeps"):
            sweep_id = row["sweep_id"]
            prefix = row["prefix"]
            download_sweep_data(sweep_id, prefix)
        return
    sweep_id_and_maybe_prefix = sweep_id_and_maybe_prefix.strip().split(" ", maxsplit=1)
    if len(sweep_id_and_maybe_prefix) == 1:
        sweep_id = sweep_id_and_maybe_prefix[0]
        prefix = None
    else:
        assert len(sweep_id_and_maybe_prefix) == 2
        sweep_id = sweep_id_and_maybe_prefix[0].strip()
        prefix = sweep_id_and_maybe_prefix[1].strip()

    # Get user input for the prefix they want to use for the downloaded files
    if prefix is None:
        prefix = input("Enter the prefix for the downloaded files: ").strip()
    # prefix = "DEBUG"

    # Download the data
    download_sweep_data(sweep_id, prefix)


def download_sweep_data(sweep_id: str, prefix: str) -> None:
    """Download the artifacts from the runs in the sweep."""
    # Initialize W&B API
    api = wandb.Api()

    # Get the sweep
    sweep = api.sweep(f"{constants.WANDB_PROJECT}/{sweep_id}")

    # Get the runs in the sweep
    runs = list(sweep.runs)

    # Download the artifacts from each run
    for run in tqdm(runs):
        if not run.state == "finished":
            print(f"Skipping run {run.id} because it is not finished")
            continue
        # Download the actions artifact
        artifact_actions = api.artifact(
            f"{constants.WANDB_PROJECT}/run-{run.id}-whole_runactions:latest"
        )
        artifact_actions.download(root=OUTPUT_FOLDER_ACTIONS)

        # Rename the "actions.table.json" in the output folder to be prefix + 'A' + run.name[-1].json
        actions_path = f"{OUTPUT_FOLDER_ACTIONS}/{prefix} A{run.name[-1]}.json"
        if os.path.exists(actions_path):
            os.remove(actions_path)
        os.rename(f"{OUTPUT_FOLDER_ACTIONS}/whole_run/actions.table.json", actions_path)
        convert_json_to_csv(actions_path)

        # Download the variables artifact
        artifact_variables = api.artifact(
            f"{constants.WANDB_PROJECT}/run-{run.id}-whole_rundynamic_vars:latest"
        )
        artifact_variables.download(root=OUTPUT_FOLDER_VARIABLES)

        # Rename the "dynamic_vars.table.json" in the output folder to be prefix + 'V' + run.name[-1].json
        vars_path = f"{OUTPUT_FOLDER_VARIABLES}/{prefix} V{run.name[-1]}.json"
        if os.path.exists(vars_path):
            os.remove(vars_path)
        os.rename(
            f"{OUTPUT_FOLDER_VARIABLES}/whole_run/dynamic_vars.table.json",
            vars_path,
        )
        convert_json_to_csv(vars_path)

    # Remove the whole_run folders
    if os.path.exists(f"{OUTPUT_FOLDER_ACTIONS}/whole_run"):
        os.rmdir(f"{OUTPUT_FOLDER_ACTIONS}/whole_run")
    if os.path.exists(f"{OUTPUT_FOLDER_VARIABLES}/whole_run"):
        os.rmdir(f"{OUTPUT_FOLDER_VARIABLES}/whole_run")


def convert_json_to_csv(json_path: str) -> None:
    """Load the JSON artifact data (assuming it's a table), save it to CSV, and delete the old JSON."""
    # Load the JSON
    with open(json_path, encoding="utf-8") as file:
        json_dict = json.load(file)
    df = pd.DataFrame(json_dict["data"], columns=json_dict["columns"])

    # Save to CSV
    csv_path = json_path.replace(".json", ".csv")
    df.to_csv(csv_path, index=False)

    # Delete the JSON
    os.remove(json_path)


if __name__ == "__main__":
    main()
