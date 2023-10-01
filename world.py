"""The global game state with settings and the ability to resolve actions."""
from data_types import Action


class World:
    """The global environment state."""

    def __init__(self, nations, action_config, max_days):
        # Imported here to avoid circular imports
        from nations import LLMNation

        self.nations: list[LLMNation] = nations
        self.action_config = action_config
        self.max_days = max_days
        self.current_day = 1
        # History of day number to list of actions taken
        self.action_history: dict[int, list[Action]] = {}
        # when prmpting the messages, includes received messages from other nations

        # clean the self.action_config, so that the column names are valid and no longer have underscoes
        # also make sure that the column names are valid

    # create a method to handle the differences of arithmetic, either multiplication or addition
    def handle_arithmetic(self, action_type, recipient_type, action, action_design):
        # fill in with logic
        pass

    def update_nation_variable(self, nation_index, variable_name, value):
        # Find the nation corresponding to nation_index or name
        # This assumes nation_index is an index, adjust if it's a name or other identifier
        nation = self.nations[nation_index]

        # Get existing value
        static_key = self.nations.get_static(variable_name)

        # call the handle arithmetic method
        value = handle_arithmetic()

        # Do math
        self.nations.set_dynamic(static_key + value)

        # Set new value

        if hasattr(nation, variable_name):
            # Assume the variable on the nation should be incremented by value
            setattr(nation, variable_name, getattr(nation, variable_name) + value)
        else:
            print(f"Invalid variable name: {variable_name} for nation {nation_index}")

    # add in the actions
    # map of day number to actions
    def update_state(self, actions: list[Action]):
        """Advance the state of the world, executing actions upon the nations."""

        # Psuedocode
        # for action in actions:
        # Match action.name to one of the action_design in the action_config
        # If the name doesn't match, log a warning and skip this action
        # For the columns in that action_design
        # If the column ends in _self or _other (meaning it affects stats)
        # Update the relevant nation variables for action.self
        # Find the nation corresponding to action.other
        # Update the relevant nation variables for action.other
        # Add the self, other, and action name to the action_history

        for action in actions:
            # Match action.name to one of the action_design in the action_config
            if action.name not in self.action_config:
                print(f"Action {action.name} not found in action config")
                continue

            action_design = self.action_config[action.name]

            # For the columns in that action_design
            for column_name in action_design.columns:
                components = column_name.split("_")
                # change this to an assertion after you think the continue
                if len(components) != 2:
                    print(f"Invalid column name: {column_name}")
                    continue  # skip to the next column

                (
                    action_type,
                    recipient_type,
                ) = components

                if recipient_type == "self":
                    # Assume action.self is the index or name of the nation in self.nations
                    # check if the action_type is arithmetic

                    # and action_design[column_name] is the value to update
                    self.update_nation_variable(action.self, action_design[column_name])

                elif recipient_type == "other":
                    # Assume action.other is the index or name of the nation in self.nations
                    # and action_design[column_name] is the value to update
                    self.update_nation_variable(
                        action.other, action_design[column_name]
                    )

            # Add action to history
            self.action_history.append(action)

        self.current_day += 1
