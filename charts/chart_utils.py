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

DEFAULT_COLOR_PALETTE = "bright"


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


def get_color_from_palette(
    index: int, palette_name: str = DEFAULT_COLOR_PALETTE
) -> Any:
    """Get a color from the default palette."""
    palette = sns.color_palette(palette_name)
    color = palette[index]
    return color


def save_plot(file_path: str) -> None:
    """Save a plot to a file."""
    create_file_dir_if_not_exists(file_path)
    plt.savefig(file_path, bbox_inches="tight", dpi=300)


def get_results_full_path(relative_path: str) -> str:
    """Given a relative path from the charts directory, return the full path."""
    return os.path.join(os.path.dirname(__file__), relative_path)


COLOR_ALT_1 = "tab:purple"
COLOR_ALT_2 = "tab:red"

CAPSIZE_DEFAULT = 0.2

MODELS_COLORS_MARKERS = [
    # ("Claude-1.2", get_color_from_palette()),
    ("Claude-2.0", get_color_from_palette(0, None), "o"),
    ("GPT-3.5", get_color_from_palette(2, None), "s"),
    ("GPT-4-Base", get_color_from_palette(1, "colorblind"), "v"),
    ("GPT-4", get_color_from_palette(4, None), "^"),
]
ALL_MODEL_NAMES = [model_name for model_name, _, _ in MODELS_COLORS_MARKERS]
MODELS_TO_COLORS = {model_name: color for model_name, color, _ in MODELS_COLORS_MARKERS}
MODELS_TO_MARKERS = {
    model_name: marker for model_name, _, marker in MODELS_COLORS_MARKERS
}

ALL_SITUATIONS = ["Neutral", "Drone", "3 Drones"]
ALL_SITUATIONS = ["Drone", "NoDescriptions", "Invasion", "WorldLLM Invasion A"]
SITUATIONS_COLORS = [
    ("Neutral", get_color_from_palette(2)),
    ("Invasion", get_color_from_palette(9)),
    ("Cyberattack", get_color_from_palette(0)),
]
ALL_SITUATIONS = [situation for situation, _ in SITUATIONS_COLORS]
SITUATION_COLORS = [color for _, color in SITUATIONS_COLORS]
SITUATIONS_TO_COLORS = {situation: color for situation, color in SITUATIONS_COLORS}

SITUATION_TO_HATCH = {
    "Neutral": "",
    "Invasion": "/",
    "Cyberattack": "x",
}
