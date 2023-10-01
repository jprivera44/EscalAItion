"""The global game state with settings and the ability to resolve actions."""

from nations import Nation
from data_types import Action


class World:
    """The global environment state."""

    def __init__(self, nations, action_config_unprocessed, max_weeks):
        self.nations: list[Nation] = nations
        # TODO process action config
        self.action_config = action_config_unprocessed
        self.max_weeks = max_weeks
        self.current_week = 0
        # History of week number to list of actions taken
        self.action_history: dict[int, list[Action]] = {}
        # when prmpting the messages, includes received messages from other nations

    def clean_config(self):
        
        #clean the self.action_config, so that the column names are valid and no longer have underscoes
        #also make sure that the column names are valid

        actions = self.action_config


        for action in actions:
            column_name = action.column_name
            components = column_name.split("_")
            assert len(components) == 2  # Column name and type (self/other)
            action_type = components[0]
            assert action_type in self.action_config
            recepient_type = components[1]
        
    
        self.action_config = actions

    # add in the actions
    # map of week number to actions
    def update_state(self, actions: list[Action]):
        """Advance the state of the world, executing actions upon the nations."""

   

            if recepient_type == "self":
                # Update the relevant nation variables
                self.nations[action_type]
                pass

            elif recepient_type == "other":
                # Update the relevant other nation variables
                pass

            pass

        self.current_week += 1
