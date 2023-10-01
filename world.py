"""The global game state with settings and the ability to resolve actions."""

from nations import Nation
from data_types import Action


class World:
    """The global environment state."""

    def __init__(self, nations, action_config, max_weeks):
        self.nations: list[Nation] = nations
        self.action_config = action_config
        self.max_weeks = max_weeks
        self.current_week = 0
        # History of week number to list of actions taken
        self.action_history: dict[int, list[Action]] = {}
        # when prmpting the messages, includes received messages from other nations

    # add in the actions
    # map of week number to actions
    def update_state(self, actions: list[Action]):
        """Advance the state of the world, executing actions upon the nations."""
        # change the variables within the nation classes
        # readin the actions from the nations
        # store the actions taken
        # loop of going through the table of a
        for action in actions:
            # Update the relevant nations
            pass

        # increase turn
        self.current_week += 1
