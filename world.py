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

    def perform_operation(self, nation_value, env_value, operator):
        """Handle the differences of arithmetic, either multiplication or addition."""
        if operator == "add":
            value = nation_value + env_value

        if operator == "mult":
            value = nation_value * (env_value + 1)

        # assert that the operator is either add or mult
        try:
            assert operator in ["add", "mult"]
        except AssertionError as msg:
            print(msg)

        return value

    def update_nation_variable(self, nation_name, variable_name, value, operator):
        # Find the nation corresponding to nation_name
        nation = [
            nation
            for nation in self.nations
            if nation.get_static("name") == nation_name
        ][0]

        # Dynamic value
        nation_value = nation.get_dynamic(variable_name)

        # call the handle arithmetic method
        dynamic_value = self.perform_operation(nation_value, value, operator)

        # clamp the dynmaic value between 0 and 10
        if variable_name == "population":
            # clamp to 0 and have no max value
            dynamic_value = max(0, dynamic_value)
        elif variable_name != "GDP":
            dynamic_value = max(0, min(10, dynamic_value))

        nation.set_dynamic(variable_name, dynamic_value)

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
            if action.name not in set(self.action_config["name"]):
                print(f"Action {action.name} not found in action config")
                continue

            # Access the row for the series
            action_design = self.action_config.loc[
                self.action_config["name"] == action.name
            ].iloc[0]

            # Add action to history
            if self.current_day not in self.action_history:
                self.action_history[self.current_day] = []

            self.action_history[self.current_day].append(action)

            # If message action, don't update any variables
            if action.name == "Message":
                continue

            # inplement nuclear locking
            # clamping dyanmic variables between 0 and 10, unless its GDP clamp to 0

            # For the columns in that action_design
            for column_name in action_design.keys():
                components = column_name.split("_")
                # change this to an assertion after you think the continue
                # change the code below to an assertion statement
                if len(components) != 3:
                    continue

                assert len(components) == 3
                # Optionally, continue to the next column or handle

                (dynamic_var_name, operator_type, recipient_type) = components

                if recipient_type == "self":
                    # Assume action.self is the index or name of the nation in self.nations
                    # check if the action_type is arithmetic
                    # and action_design[column_name] is the value to update
                    # def update_nation_variable(self, nation_index, variable_name, value, operator):
                    self.update_nation_variable(
                        action.self,
                        dynamic_var_name,
                        action_design[column_name],
                        operator_type,
                    )

                elif recipient_type == "other":
                    # Assume action.other is the index or name of the nation in self.nations
                    # and action_design[column_name] is the value to update
                    self.update_nation_variable(
                        action.other,
                        dynamic_var_name,
                        action_design[column_name],
                        operator_type,
                    )

        self.current_day += 1
