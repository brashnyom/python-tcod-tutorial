import tcod

from typing import List
from map_objects.game_map import GameMap
from entity import Entity
from components.fighter import Fighter
from components.inventory import Inventory
from render_functions import RenderOrder
from game_messages import MessageLog
from game_states import GameStates


def get_config():
    config = {
        "window_title": "Roguelike Tutorial Revised",
        "screen_width": 80,
        "screen_height": 50,

        "bar_width": 20,
        "panel_height": 7,

        "map_width": 80,
        "map_height": 43,

        "room_max_size": 10,
        "room_min_size": 6,
        "max_rooms": 30,

        "fov_algorithm": 0,
        "fov_light_walls": True,
        "fov_radius": 10,

        "max_monsters_per_room": 3,
        "max_items_per_room": 2,

        "colors": {
            "dark_wall": tcod.Color(0, 0, 100),
            "dark_ground": tcod.Color(50, 50, 150),
            "light_wall": tcod.Color(130, 110, 50),
            "light_ground": tcod.Color(200, 180, 50),
        }
    }

    config["panel_y"] = config["screen_height"] - config["panel_height"]
    config["message_x"] = config["bar_width"] + 2
    config["message_width"] = config["screen_width"] - config["message_x"]
    config["message_height"] = config["panel_height"] - 1

    return config


def get_game_variables(config):
    game_map: GameMap = GameMap(config["map_width"], config["map_height"])
    entities: List[Entity] = list()

    game_map.make_map(
        config["max_rooms"], config["room_min_size"], config["room_max_size"]
    )

    player_fighter_component: Fighter = Fighter(30, 2, 5)
    player_inventory_component: Inventory = Inventory(26)
    player: Entity = Entity(
        int(config["screen_width"] / 2),
        int(config["screen_height"] / 2),
        "@",
        tcod.white,
        "player",
        RenderOrder.ACTOR,
        True,
        player_fighter_component,
        inventory=player_inventory_component
    )
    entities.append(player)

    player.x, player.y = game_map.rooms[0].center

    game_map.populate_map(
        entities, config["max_monsters_per_room"], config["max_items_per_room"]
    )

    message_log: MessageLog = MessageLog(
        config["message_x"], config["message_width"], config["message_height"]
    )

    game_state: GameStates = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state
