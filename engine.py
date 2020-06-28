import tcod
import numpy as np

from typing import Optional

from actions import Action, ActionType
from input_handlers import handle_keys, handle_keys_main_menu
from entity import Entity, get_blocking_entity_at, get_entities_at
from render_functions import render_terrain, render_entities, \
    render_player_stats, render_message_log, render_inventory
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_player, kill_monster
from game_messages import Message
from loader_functions.initialize_new_game import get_config, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box


def play_game(
    context, config, player, entities, game_map,
    message_log, game_state, console, panel
):
    fov_recompute: bool = True

    targeting_item: Entity = None
    targeting_x: int = 0
    targeting_y: int = 0

    previous_game_state: GameStates = game_state

    fov_map: tcod.map.Map = initialize_fov(game_map)

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
                save_game(player, entities, game_map, message_log, game_state)
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
                        save_game(player, entities, game_map, message_log, game_state)
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


def main():
    config = get_config()

    tilesheet = tcod.tileset.load_tilesheet(
        "Codepage-437.png", 32, 8, tcod.tileset.CHARMAP_CP437
    )
    console = tcod.Console(config["screen_width"], config["screen_height"])
    panel = tcod.Console(config["screen_width"], config["panel_height"])

    player = None
    entities = list()
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    new_game = None
    load_saved_game = None
    exit_game = None

    main_menu_background_image = tcod.image.Image.from_array(
        np.zeros((5, 5, 3), dtype=np.uint8)
    )

    with tcod.context.new_terminal(
        console.width, console.height, tileset=tilesheet, title=config["window_title"]
    ) as context:
        while True:
            if show_main_menu:
                main_menu(console, main_menu_background_image)
                if show_load_error_message:
                    message_box(console, "No save game to load!", 50)

                context.present(console, integer_scaling=True)

                if (
                    show_load_error_message
                    and (new_game or load_saved_game or exit_game)
                ):
                    show_load_error_message = False
                elif new_game:
                    player, entities, game_map, \
                        message_log, game_state = get_game_variables(config)
                    game_state = GameStates.PLAYERS_TURN
                    show_main_menu = False
                elif load_saved_game:
                    try:
                        player, entities, game_map, \
                            message_log, game_state = load_game()
                        show_main_menu = False
                    except FileNotFoundError:
                        show_load_error_message = True
                elif exit_game:
                    break
            else:
                console.clear()
                play_game(
                    context, config, player, entities, game_map,
                    message_log, game_state, console, panel
                )
                show_main_menu = True

            for event in tcod.event.wait():
                context.convert_event(event)
                if event.type == "QUIT":
                    raise SystemExit()
                if event.type == "KEYDOWN":
                    action = handle_keys_main_menu(event.sym)
                    if action:
                        new_game = action.action_type == ActionType.NEW_GAME
                        load_saved_game = action.action_type == ActionType.LOAD_GAME
                        exit_game = action.action_type == ActionType.ESCAPE


if __name__ == "__main__":
    main()
