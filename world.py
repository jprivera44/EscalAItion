"""The global game state with settings and the ability to resolve actions."""

from nations import Nation
from data_types import Action


class World:
    """The global environment state."""

    def __init__(self, nations, action_config, max_days):
        self.nations: list[Nation] = nations
        # TODO process action config
        self.action_config = action_config
        self.max_days = max_days
        self.current_week = 0
        # History of week number to list of actions taken
        self.action_history: dict[int, list[Action]] = {}
        # when prmpting the messages, includes received messages from other nations

        # clean the self.action_config, so that the column names are valid and no longer have underscoes
        # also make sure that the column names are valid

    def update_variable(self, variable_name: str, value: str):
        if hasattr(self, variable_name):
            current_value = getattr(self, variable_name)
            new_value = self.convert_value(value, type(current_value))
            setattr(self, variable_name, new_value)
        else:
            raise ValueError(f"Invalid variable name: {variable_name}")

    @staticmethod
    def convert_value(value: str, data_type: type) -> any:
        if data_type == int:
            return int(value)
        elif data_type == float:
            return float(value.strip("%")) / 100 if "%" in value else float(value)

        else:
            return value  # Return value as-is if data type is not recognized

    # add in the actions
    # map of week number to actions
    def update_state(self, actions: list[Action]):
        """Advance the state of the world, executing actions upon the nations."""

        for action in actions:
            column_name = action.column_name
            components = column_name.split("_")
            assert len(components) == 2  # Column name and type (self/other)
            action_type = components[0]
            assert action_type in self.action_config
            recepient_type = components[1]

            if recepient_type == "self":
                # Update the relevant nation variables

                # create a for loop that goes through the nations and updates the variables
                for nation in self.nations:
                    if nation.name == action_type:
                nation.update_variable(action.column_name, action.value)
                        

                pass

            elif recepient_type == "other":
                # Update the relevant other nation variables
                self.nations
                pass

            pass

        self.current_week += 1
