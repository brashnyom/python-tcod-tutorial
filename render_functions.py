import tcod

from typing import List
from enum import Enum
from entity import Entity


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def render_player_stats(con, player: Entity):
    con.print(
        1,
        con.height - 2,
        f"{player.fighter.hp}/{player.fighter.max_hp} HP"  # type: ignore
    )


def render_terrain(con, game_map, fov_map: tcod.map.Map, colors: dict):
    # TODO Add typing hints for GameMap without circular dependency
    for x in range(0, game_map.width):
        for y in range(0, game_map.height):
            # TODO FIXME Exploration should probably be decoupled from this
            visible = fov_map.fov[x][y]
            wall = game_map.tiles[x][y].blocked

            if visible:
                game_map.tiles[x][y].explored = True

            if not game_map.tiles[x][y].explored:
                continue

            if wall:
                string = "\u2588"  # solid block
                color = "light_wall" if visible else "dark_wall"
            else:
                string = "."
                color = "light_ground" if visible else "dark_ground"
            con.print(x=x, y=y, string=string, fg=colors[color])


def render_entities(con, entities: List[Entity], fov_map: tcod.map.Map):
    for entity in sorted(entities, key=lambda e: e.render_order.value):
        if fov_map.fov[entity.x][entity.y]:
            render_entity(con, entity)


def render_entity(con, entity: Entity):
    con.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)
