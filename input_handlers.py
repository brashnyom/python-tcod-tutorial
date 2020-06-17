import tcod.event

from actions import ActionType, Action


def handle_keys(key) -> [Action, None]:
    action = None

    if key == tcod.event.K_UP:
        action = Action(ActionType.MOVEMENT, dx=0, dy=-1)
    elif key == tcod.event.K_DOWN:
        action = Action(ActionType.MOVEMENT, dx=0, dy=1)
    elif key == tcod.event.K_LEFT:
        action = Action(ActionType.MOVEMENT, dx=-1, dy=0)
    elif key == tcod.event.K_RIGHT:
        action = Action(ActionType.MOVEMENT, dx=1, dy=0)

    elif key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)

    return action
