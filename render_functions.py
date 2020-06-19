import tcod

from typing import List
from entity import Entity
from map_objects.game_map import GameMap


def render_terrain(con, game_map: GameMap, fov_map: tcod.map.Map, colors: dict):
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
                string = "X"
                color = "light_wall" if visible else "dark_wall"
            else:
                string = "."
                color = "light_ground" if visible else "dark_ground"
            con.print(x=x, y=y, string=string, fg=colors[color])


def render_entities(con, entities: List[Entity], fov_map: tcod.map.Map):
    for entity in entities:
        if fov_map.fov[entity.x][entity.y]:
            render_entity(con, entity)


def render_entity(con, entity: Entity):
    con.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)
