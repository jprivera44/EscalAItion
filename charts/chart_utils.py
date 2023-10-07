"""
Functions to help with creating charts.
"""

import os
import json
import random
from typing import Any

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def set_seed(seed: int) -> None:
    """Set the seed for numpy and tensorflow."""
    random.seed(seed)
    np.random.seed(seed)


def load_json(file_path: str) -> dict[str, Any]:
    """Load a JSON file of a given path (absolute or relative to cwd)."""
    with open(file_path, encoding="utf-8") as file:
        file_data = json.load(file)
    assert isinstance(file_data, dict)
    return file_data


def create_file_dir_if_not_exists(file_path: str) -> None:
    """Create the directory for a file if it doesn't already exist."""
    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)


def initialize_plot_default() -> None:
    """Set default plot styling."""
    # Set seed
    set_seed(66)
    # Default theme
    sns.set_theme(context="paper", font_scale=1.5, style="whitegrid")
    # Figure size
    plt.rcParams["figure.figsize"] = (8, 5)
    # Make title larger
    plt.rcParams["axes.titlesize"] = 16
    # Higher DPI
    plt.rcParams["figure.dpi"] = 450
    # Default marker
    plt.rcParams["lines.marker"] = "o"
    # Default marker size
    plt.rcParams["lines.markersize"] = 12
    # Accessible colors
    sns.set_palette(DEFAULT_COLOR_PALETTE)


def initialize_plot_bar() -> None:
    """Set default plot styling for bar charts."""
    initialize_plot_default()
    # No markers
    plt.rcParams["lines.marker"] = ""


def get_color_from_palette(index: int) -> Any:
    """Get a color from the default palette."""
    palette = sns.color_palette(DEFAULT_COLOR_PALETTE)
    color = palette[index]
    return color


def save_plot(file_path: str) -> None:
    """Save a plot to a file."""
    create_file_dir_if_not_exists(file_path)
    plt.savefig(file_path, bbox_inches="tight", dpi=300)


def get_results_full_path(relative_path: str) -> str:
    """Given a relative path from the charts directory, return the full path."""
    return os.path.join(os.path.dirname(__file__), relative_path)


DEFAULT_COLOR_PALETTE = "bright"

COLOR_ALT_1 = "tab:purple"
COLOR_ALT_2 = "tab:red"

CAPSIZE_DEFAULT = 0.2
