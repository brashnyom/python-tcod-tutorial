import tcod

from typing import List
from enum import Enum, auto
from entity import Entity
from game_messages import MessageLog
from menus import inventory_menu, level_up_menu, character_screen
from game_states import GameStates


class RenderOrder(Enum):
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


def render_character_screen(con, game_state, player):
    if game_state == GameStates.CHARACTER_SCREEN:
        character_screen(con, player, 30, 10)


def render_level_up_menu(con, game_state, player, menu_width: int):
    if game_state == GameStates.LEVEL_UP:
        header = "Level up! Choose a stat to raise: "
        level_up_menu(con, header, player, menu_width)


def render_inventory(con, game_state, player, inventory_width: int):
    if game_state == GameStates.SHOW_INVENTORY:
        header = \
            "Press the key next to an item to use it, or Esc to cancel.\n"
    else:
        header = \
            "Press the key next to an item to drop it, or Esc to cancel.\n"
    inventory_menu(con, header, player, inventory_width)


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


def render_dungeon_level(con, game_map):
    con.print(
        1, 3, f"Dungeon level: {game_map.dungeon_level}", tcod.white,
        alignment=tcod.LEFT
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


def render_entities(con, entities: List[Entity], game_map, fov_map: tcod.map.Map):
    for entity in sorted(entities, key=lambda e: e.render_order.value):
        is_stairs = bool(entity.stairs is not None)
        is_explored = game_map.tiles[entity.x][entity.y].explored
        if fov_map.fov[entity.x][entity.y] or (is_stairs and is_explored):
            render_entity(con, entity)


def render_entity(con, entity: Entity):
    con.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)
