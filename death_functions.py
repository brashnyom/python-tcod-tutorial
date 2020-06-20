import tcod

from typing import Tuple
from game_states import GameStates
from entity import Entity
from render_functions import RenderOrder


def kill_player(player: Entity) -> Tuple[str, GameStates]:
    player.char = "%"
    player.color = tcod.dark_red

    return "You died!", GameStates.PLAYER_DEAD


def kill_monster(monster: Entity) -> str:
    message = f"The {monster.name} dies!"
    monster.char = "%"
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f"remains of {monster.name}"
    monster.render_order = RenderOrder.CORPSE
    return message
