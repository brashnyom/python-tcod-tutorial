import tcod.event

from typing import Optional
from actions import ActionType, Action
from game_states import GameStates


def handle_keys(key, game_state: GameStates) -> Optional[Action]:
    action = None
    if game_state == GameStates.PLAYERS_TURN:
        action = handle_keys_player_turn(key)
    elif game_state == GameStates.PLAYER_DEAD:
        action = handle_keys_player_dead(key)
    elif game_state == GameStates.SHOW_INVENTORY:
        action = handle_keys_inventory(key)
    elif game_state == GameStates.DROP_INVENTORY:
        action = handle_keys_inventory(key)
    elif game_state == GameStates.TARGETING:
        action = handle_keys_targeting(key)
    elif game_state == GameStates.EXAMINE:
        action = handle_keys_targeting(key)
    elif game_state == GameStates.LEVEL_UP:
        action = handle_keys_level_up_menu(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        action = handle_keys_character_screen(key)
    return action


def handle_keys_player_turn(key) -> Optional[Action]:
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
    elif key == tcod.event.K_z:
        action = Action(ActionType.WAIT)
    elif key == tcod.event.K_g:
        action = Action(ActionType.PICKUP)
    elif key == tcod.event.K_i:
        action = Action(ActionType.SHOW_INVENTORY)
    elif key == tcod.event.K_d:
        action = Action(ActionType.DROP_INVENTORY)
    elif key == tcod.event.K_t:
        action = Action(ActionType.TAKE_STAIRS)
    elif key == tcod.event.K_x:
        action = Action(ActionType.EXAMINE)
    elif key == tcod.event.K_c:
        action = Action(ActionType.SHOW_STATS)
    elif key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)

    return action


def handle_keys_player_dead(key) -> Optional[Action]:
    action = None

    if key == tcod.event.K_i:
        action = Action(ActionType.SHOW_INVENTORY)
    elif key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)

    return action


def handle_keys_inventory(key) -> Optional[Action]:
    action = None

    index: int = key - ord("a")

    if index >= 0:
        action = Action(ActionType.SELECT_ITEM, item_index=index)
    elif key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)

    return action


def handle_keys_targeting(key) -> Optional[Action]:
    action = None

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
    elif key == tcod.event.K_f:
        action = Action(ActionType.SELECT_TARGET)
    elif key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)

    return action


def handle_keys_level_up_menu(key) -> Optional[Action]:
    action = None
    if key == tcod.event.K_a:
        action = Action(ActionType.RAISE_STAT, stat="hp")
    elif key == tcod.event.K_b:
        action = Action(ActionType.RAISE_STAT, stat="str")
    elif key == tcod.event.K_c:
        action = Action(ActionType.RAISE_STAT, stat="def")
    return action


def handle_keys_character_screen(key) -> Optional[Action]:
    action = None
    if key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)
    return action


def handle_keys_main_menu(key) -> Optional[Action]:
    action = None
    if key == tcod.event.K_a:
        action = Action(ActionType.NEW_GAME)
    elif key == tcod.event.K_b:
        action = Action(ActionType.LOAD_GAME)
    elif key == tcod.event.K_c or key == tcod.event.K_ESCAPE:
        action = Action(ActionType.ESCAPE)
    return action
