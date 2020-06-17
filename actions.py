from enum import Enum


class ActionType(Enum):
    ESCAPE = 1
    MOVEMENT = 2


class Action:
    def __init__(self, action_type: ActionType, **kwargs):
        self.action_type: ActionType = action_type
        self.kwargs = kwargs
