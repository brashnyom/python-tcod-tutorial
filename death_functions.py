import tcod

from typing import Tuple
from game_states import GameStates
from entity import Entity
from render_functions import RenderOrder
from game_messages import Message


def kill_player(player: Entity) -> Tuple[Message, GameStates]:
    player.char = "%"
    player.color = tcod.dark_red

    return Message("You died!", tcod.red), GameStates.PLAYER_DEAD


def kill_monster(monster: Entity) -> Message:
    message: Message = Message(f"The {monster.name} dies!", tcod.orange)
    monster.char = "%"
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = f"remains of {monster.name}"
    monster.render_order = RenderOrder.CORPSE
    return message
