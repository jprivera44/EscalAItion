"""The global game state with settings and the ability to resolve actions."""

from nations import Nation


class World(nation, action_spec):
    """The global environment state."""

    nations: list[Nation]

    # include actions such as
    # communicating to the nations

    # TODO
    self.action_spec = action_spec
    self.max_weeks = max_weeks
    self.current_week = 0
