"""The global game state with settings and the ability to resolve actions."""
from data_types import Action

import wandb

import prompts


class World:
    """The global environment state."""

    def __init__(self, logger, nations, action_config, max_days):
        # Imported here to avoid circular imports
        from nations import LLMNation

        self.logger = logger
        self.nations: list[LLMNation] = nations
        self.action_config = action_config
        self.max_days = max_days
        self.current_day = 1
        # History of day number to list of actions taken
        self.action_history: dict[int, list[Action]] = {}
        # History of the World Model's summaries of the consequences of what happened on each day
        # Tuple contains (summary, system_prompt, user_prompt)
        self.consequence_history: dict[int, tuple[str, str, str]] = {}

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

    def update_nation_variable(self, nation_name, variable_name, delta, operator):
        """Update the dynamic variable of a nation."""
        # Find the nation corresponding to nation_name
        nation = [
            nation
            for nation in self.nations
            if nation.get_static("name") == nation_name
        ][0]

        # Dynamic value
        old_value = nation.get_dynamic(variable_name)

        # call the handle arithmetic method
        new_value = self.perform_operation(old_value, delta, operator)

        if variable_name == "nuclear":
            # clamp the dynmaic value between 0 and 10
            new_value = max(0, min(10, new_value))
        elif variable_name == "population":
            # clamp to 0 and have no max value
            new_value = max(0, new_value)
        elif variable_name != "gdp":
            # GDP is unclamped
            if wandb.config.clamp_dynamic_variables:
                new_value = max(0, min(10, new_value))

        nation.set_dynamic(variable_name, new_value)

    def update_state(self, actions: list[Action]):
        """Advance the state of the world, executing actions upon the nations."""

        for action in actions:
            # Match action.name to one of the action_design in the action_config
            if action.name not in set(self.action_config["name"]):
                self.logger.warning(f"Action {action.name} not found in action config")
                continue

            # Check for invalid other nation
            if action.other not in [
                nation.get_static("name") for nation in self.nations
            ]:
                if (
                    action.name == "Message" and action.other != "World"
                ) or action.name != "Message":
                    self.logger.warning(
                        f"Action {action.name} has invalid other nation {action.other}"
                    )
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

        # Summarize the consequences of each action
        system_prompt = prompts.get_world_model_system_prompt(world=self)
        user_prompt = prompts.get_world_model_user_prompt(world=self)
        summary = "TODO placeholder, will replace with llm later"

        self.consequence_history[self.current_day] = (
            summary,
            system_prompt,
            user_prompt,
        )

        self.current_day += 1
