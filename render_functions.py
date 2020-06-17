import tcod

from typing import List
from entity import Entity
from map_objects.game_map import GameMap


def render_all(con, game_map: GameMap, entities: List[Entity], colors: dict):
    con.clear()

    for x in range(0, game_map.width):
        for y in range(0, game_map.height):

            wall = game_map.tiles[x][y].blocked
            if wall:
                con.print(x=x, y=y, string="X", fg=colors["dark_wall"])
            else:
                con.print(x=x, y=y, string=".", fg=colors["dark_ground"])

    for entity in entities:
        render_entity(con, entity)

    tcod.console_flush()


def render_entity(con, entity):
    con.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)
