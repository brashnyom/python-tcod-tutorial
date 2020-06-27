import tcod

from typing import List, Optional

from actions import Action, ActionType
from input_handlers import handle_keys
from entity import Entity, get_blocking_entity_at, get_entities_at
from render_functions import render_terrain, render_entities, \
    render_player_stats, render_message_log, render_inventory, RenderOrder
from fov_functions import initialize_fov, recompute_fov
from map_objects.game_map import GameMap
from game_states import GameStates
from components.fighter import Fighter
from components.inventory import Inventory
from death_functions import kill_player, kill_monster
from game_messages import Message, MessageLog


# TODO Restore examining entities on tile
restore = get_entities_at  # supress flake8 warning temp hack


def init_config():
    config = {
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


def main():
    config = init_config()

    game_map: GameMap = GameMap(config["map_width"], config["map_height"])
    entities: List[Entity] = list()

    game_map.make_map(
        config["max_rooms"], config["room_min_size"], config["room_max_size"]
    )

    player_fighter_component: Fighter = Fighter(30, 2, 5)
    player_inventory_component: Inventory = Inventory(25)
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

    fov_recompute: bool = True
    fov_map: tcod.map.Map = initialize_fov(game_map)

    game_state: GameStates = GameStates.PLAYERS_TURN
    previous_game_state: GameStates = game_state

    tilesheet = tcod.tileset.load_tilesheet(
        "Codepage-437.png", 32, 8, tcod.tileset.CHARMAP_CP437
    )

    console = tcod.Console(config["screen_width"], config["screen_height"])
    panel = tcod.Console(config["screen_width"], config["panel_height"])

    targeting_item: Entity = None
    targeting_x: int = 0
    targeting_y: int = 0

    with tcod.context.new_terminal(
        console.width, console.height, tileset=tilesheet, title="roguelike tutorial"
    ) as context:
        while True:
            player_turn_results = list()

            if fov_recompute:
                recompute_fov(
                    fov_map,
                    player.x,
                    player.y,
                    config["fov_radius"],
                    config["fov_light_walls"],
                    config["fov_algorithm"]
                )
                fov_recompute = False

            console.clear()
            panel.clear()

            # TODO We probably don't need to call render_terrain on every loop
            render_terrain(console, game_map, fov_map, config["colors"])
            render_entities(console, entities, fov_map)
            render_player_stats(panel, config["bar_width"], player)
            render_message_log(panel, message_log)
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                render_inventory(console, game_state, player.inventory, 50)
            if game_state in (GameStates.TARGETING, GameStates.EXAMINE):
                console.draw_rect(
                    targeting_x, targeting_y, 1, 1, 0,
                    fg=(0, 0, 0), bg=(255, 255, 0)
                )

            panel.blit(
                console,
                0,
                config["panel_y"],
                0,
                0,
                config["screen_width"],
                config["panel_height"]
            )
            context.present(console, integer_scaling=True)

            if game_state == GameStates.ENEMY_TURN:
                for entity in entities:
                    if entity.ai is not None:
                        enemy_turn_results = entity.ai.take_turn(
                            player, fov_map, game_map, entities
                        )

                        for enemy_turn_result in enemy_turn_results:
                            if "message" in enemy_turn_result:
                                message_log.add_message(enemy_turn_result["message"])
                            if "dead" in enemy_turn_result:
                                if enemy_turn_result["dead"] is player:
                                    message, game_state = kill_player(
                                        enemy_turn_result["dead"]
                                    )
                                    message_log.add_message(message)
                                else:
                                    message_log.add_message(
                                        kill_monster(enemy_turn_result["dead"])
                                    )
                            if game_state == GameStates.PLAYER_DEAD:
                                break
                        if game_state == GameStates.PLAYER_DEAD:
                            break
                else:
                    game_state = GameStates.PLAYERS_TURN

            for event in tcod.event.wait():
                context.convert_event(event)
                if event.type == "QUIT":
                    raise SystemExit()
                elif event.type == "KEYDOWN":
                    action: [Action, None] = handle_keys(event.sym, game_state)
                    if action is None:
                        continue
                    action_type: ActionType = action.action_type

                    if (
                        action_type == ActionType.MOVEMENT
                        and game_state == GameStates.PLAYERS_TURN
                    ):
                        dx: int = action.kwargs.get("dx", 0)
                        dy: int = action.kwargs.get("dy", 0)
                        new_x: int = player.x + dx
                        new_y: int = player.y + dy

                        if not game_map.is_blocked(new_x, new_y):
                            blocking_entity: Optional[Entity] = get_blocking_entity_at(
                                new_x, new_y, entities
                            )
                            if blocking_entity is not None:
                                player_turn_results.extend(
                                    player.fighter.attack(blocking_entity)
                                )
                            else:
                                player.move(dx, dy)
                                fov_recompute = True
                        game_state = GameStates.ENEMY_TURN
                    elif (
                        action_type == ActionType.MOVEMENT
                        and game_state in (GameStates.TARGETING, GameStates.EXAMINE)
                    ):
                        dx: int = action.kwargs.get("dx", 0)
                        dy: int = action.kwargs.get("dy", 0)
                        targeting_x += dx
                        targeting_y += dy
                        if (
                            game_state == GameStates.EXAMINE
                            and fov_map.fov[targeting_x][targeting_y]
                        ):
                            location_entities = get_entities_at(
                                targeting_x, targeting_y, entities
                            )
                            if location_entities:
                                msg = ', '.join(
                                    map(lambda e: e.name, location_entities)
                                )
                                message_log.add_message(
                                    Message(f"You see here: {msg}", tcod.gray)
                                )
                    elif (
                        action_type == ActionType.PICKUP
                        and game_state == GameStates.PLAYERS_TURN
                    ):
                        for entity in entities:
                            if (
                                entity.item
                                and entity.x == player.x and entity.y == player.y
                            ):
                                pickup_results = player.inventory.add_item(entity)
                                player_turn_results.extend(pickup_results)
                                break
                        else:
                            message_log.add_message(
                                Message("There is nothing here to pick up.",
                                        tcod.yellow)
                            )
                    elif action_type == ActionType.SHOW_INVENTORY:
                        if game_state != GameStates.SHOW_INVENTORY:
                            previous_game_state = game_state
                        game_state = GameStates.SHOW_INVENTORY
                    elif action_type == ActionType.DROP_INVENTORY:
                        if game_state != GameStates.DROP_INVENTORY:
                            previous_game_state = game_state
                        game_state = GameStates.DROP_INVENTORY
                    elif action_type == ActionType.SELECT_ITEM:
                        if previous_game_state != GameStates.PLAYER_DEAD:
                            idx = action.kwargs.get("item_index", 0)
                            if idx < len(player.inventory.items):
                                item = player.inventory.items[idx]
                                if game_state == GameStates.SHOW_INVENTORY:
                                    player_turn_results.extend(
                                        player.inventory.use(
                                            item, entities=entities, fov_map=fov_map
                                        )
                                    )
                                if game_state == GameStates.DROP_INVENTORY:
                                    player_turn_results.extend(
                                        player.inventory.drop(item)
                                    )
                    elif (
                        game_state == GameStates.TARGETING
                        and action_type == ActionType.SELECT_TARGET
                    ):
                        player_turn_results.extend(
                            player.inventory.use(
                                targeting_item,
                                entities=entities,
                                fov_map=fov_map,
                                target_x=targeting_x,
                                target_y=targeting_y
                            )
                        )
                    elif (
                        game_state == GameStates.PLAYERS_TURN
                        and action_type == ActionType.EXAMINE
                    ):
                        targeting_x, targeting_y = player.x, player.y
                        game_state = GameStates.EXAMINE
                    elif action_type == ActionType.ESCAPE:
                        if game_state == GameStates.SHOW_INVENTORY:
                            game_state = previous_game_state
                        elif game_state in (GameStates.TARGETING, GameStates.EXAMINE):
                            player_turn_results.append({"targeting_cancelled": True})
                        else:
                            raise SystemExit()

            for player_turn_result in player_turn_results:
                if "message" in player_turn_result:
                    message_log.add_message(player_turn_result["message"])
                if "dead" in player_turn_result:
                    if player_turn_result["dead"] is player:
                        message, game_state = kill_player(
                            player_turn_result["dead"]
                        )
                        message_log.add_message(message)
                    else:
                        message_log.add_message(
                            kill_monster(player_turn_result["dead"])
                        )
                if "item_added" in player_turn_result:
                    entities.remove(player_turn_result["item_added"])
                    game_state = GameStates.ENEMY_TURN
                if "consumed" in player_turn_result:
                    game_state = GameStates.ENEMY_TURN
                if "item_dropped" in player_turn_result:
                    entities.append(player_turn_result["item_dropped"])
                    game_state = GameStates.ENEMY_TURN
                if "targeting" in player_turn_result:
                    game_state = GameStates.TARGETING
                    targeting_item = player_turn_result["targeting"]
                    targeting_x, targeting_y = player.x, player.y
                    message_log.add_message(targeting_item.item.targeting_message)
                if "targeting_cancelled" in player_turn_result:
                    game_state = GameStates.PLAYERS_TURN
                    message_log.add_message(Message("Targeting cancelled.", tcod.white))


if __name__ == "__main__":
    main()
