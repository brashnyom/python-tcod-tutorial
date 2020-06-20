import tcod.event

from typing import Optional
from actions import ActionType, Action


def handle_keys(key) -> Optional[Action]:
    action = None

    # TODO Transfer this into a dictionary (event key -> action)
    if key == tcod.event.K_UP or key == tcod.event.K_k:
        action = Action(ActionType.MOVEMENT, dx=0, dy=-1)
    elif key == tcod.event.K_DOWN or key == tcod.event.K_j:
        action = Action(ActionType.MOVEMENT, dx=0, dy=1)
    elif key == tcod.event.K_LEFT or key == tcod.event.K_h:
        action = Action(ActionType.MOVEMENT, dx=-1, dy=0)
    elif key == tcod.event.K_RIGHT or key == tcod.event.K_l:
        action = Action(ActionType.MOVEMENT, dx=1, dy=0)
    elif key == tcod.event.K_y:
        action = Action(ActionType.MOVEMENT, dx=-1, dy=-1)
    elif key == tcod.event.K_u:
        action = Action(ActionType.MOVEMENT, dx=1, dy=-1)
    elif key == tcod.event.K_b:
        action = Action(ActionType.MOVEMENT, dx=-1, dy=1)
    elif key == tcod.event.K_n:
        action = Action(ActionType.MOVEMENT, dx=1, dy=1)

    elif key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)

    return action
