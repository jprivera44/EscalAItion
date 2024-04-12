"""
Rename the numbers on the ends of sweep runs for later downloading.

Assumes the expected run count R is the total number of runs, and that the N runs found in the given
sweep are the last N runs (previous runs are not available in the sweep API). Thus, it will rename
the N runs in the sweep to be R - N + 1, R - N + 2, ..., R.
"""

import os
import json

import pandas as pd
from tqdm import tqdm
import wandb
from wandb.apis.public import Run, Sweep

import constants


def main():
    r"""
    Main function to rename the runs.

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
        "Enter either:\n\t1. The sweep ID\n\t2. A path to a CSV text file with 'sweep_id' and 'prefix' columns\n"
    )
    if sweep_id_and_maybe_prefix.endswith(".csv"):
        df = pd.read_csv(sweep_id_and_maybe_prefix)
        for _, row in tqdm(df.iterrows(), total=len(df), desc="🧹 Sweeps"):
            sweep_id = row["sweep_id"]
            reindex_runs(sweep_id)
        return
    sweep_id_and_maybe_prefix = sweep_id_and_maybe_prefix.strip().split(" ", maxsplit=1)
    if len(sweep_id_and_maybe_prefix) == 1:
        sweep_id = sweep_id_and_maybe_prefix[0]
    else:
        assert len(sweep_id_and_maybe_prefix) == 2
        sweep_id = sweep_id_and_maybe_prefix[0].strip()

    # Download the data
    reindex_runs(sweep_id)


def reindex_runs(sweep_id: str) -> None:
    """Download the artifacts from the runs in the sweep."""
    # Initialize W&B API
    api = wandb.Api()

    # Get the sweep
    sweep: Sweep = api.sweep(f"{constants.WANDB_PROJECT}/{sweep_id}")

    # Get the runs in the sweep
    runs = list(sweep.runs)

    # Get the total number of runs
    max_number = sweep.expected_run_count

    # Download the artifacts from each run
    run: Run
    for run_index, run in tqdm(enumerate(runs), total=len(runs), desc="🏎️ Runs"):
        if not run.state == "finished":
            print(f"Skipping run {run.id} because it is not finished")
            continue

        # Decide on the new number for this run
        new_index = max_number - run_index  # 1-indexed

        # Remove the number from the end of the run and replace it with the new number
        new_name = run.name.rsplit("-", maxsplit=1)[0] + f"-{new_index}"

        # Rename the run
        run.name = new_name
        run.update()


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
