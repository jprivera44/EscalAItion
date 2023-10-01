"""Utility functions."""

import random
import time
from typing import Any

import numpy as np

import wandb


def set_seed(seed: int) -> None:
    """Set the seed for all random number generators."""
    random.seed(seed)
    np.random.seed(seed)
    # torch.manual_seed(seed)
    # torch.cuda.manual_seed_all(seed)


def format_actions(response):
    """Pretty print a list of actions."""
    return "\n\t".join(
        [
            f"- {action.self} -> {action.other} : {action.name} {action.content}"
            for action in response.actions
        ]
    )


def remove_duplicates_keep_order(lst: list[Any]) -> list[Any]:
    """Remove duplicates from a list while preserving order (keep last occurance)."""
    return list(dict.fromkeys(reversed(lst)))[::-1]


def sleep_if_mock_wandb():
    """Sleep to avoid wandb losing data."""
    if (
        not isinstance(wandb.run.mode, wandb.sdk.lib.disabled.RunDisabled)
        and wandb.config.nation_model == "mock"
    ):
        time.sleep(5)
