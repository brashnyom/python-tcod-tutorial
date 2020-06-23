import tcod

from typing import List
from enum import Enum
from entity import Entity
from game_messages import MessageLog


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def render_message_log(con, message_log: MessageLog):
    for line_y, message in enumerate(message_log.messages):
        con.print(message_log.x, line_y + 1, message.text, message.color)


def render_bar(
    con,
    x: int,
    y: int,
    total_width: int,
    name: str,
    value: int,
    maximum: int,
    bar_color,
    back_color
):
    bar_width: int = int(float(value) / maximum * total_width)
    con.draw_rect(x, y, total_width, 1, 0, None, back_color)
    if bar_width > 0:
        con.draw_rect(x, y, bar_width, 1, 0, None, bar_color)
    con.print(
        x + int(total_width / 2), y, f"{name}: {value}/{maximum}", tcod.white,
        alignment=tcod.CENTER
    )


def render_player_stats(con, bar_width: int, player: Entity):
    # TODO Fix Optional[Fighter] mypy errors
    render_bar(
        con, 1, 1, bar_width, "HP",
        player.fighter.hp, player.fighter.max_hp,  # type: ignore
        tcod.light_red, tcod.darker_red
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
