import tcod

from typing import List, Optional

from actions import Action, ActionType
from input_handlers import handle_keys
from entity import Entity, get_blocking_entity_at, get_entities_at
from render_functions import render_terrain, render_entities, \
    render_player_stats, render_message_log, RenderOrder
from fov_functions import initialize_fov, recompute_fov
from map_objects.game_map import GameMap
from game_states import GameStates
from components.fighter import Fighter
from death_functions import kill_player, kill_monster
from game_messages import Message, MessageLog


def main():
    screen_width: int = 80
    screen_height: int = 50

    bar_width: int = 20
    panel_height: int = 7
    panel_y: int = screen_height - panel_height

    message_x: int = bar_width + 2
    message_width: int = screen_width - message_x
    message_height: int = panel_height - 1

    map_width: int = 80
    map_height: int = 43

    room_max_size: int = 10
    room_min_size: int = 6
    max_rooms: int = 30

    fov_algorithm: int = 0
    fov_light_walls: bool = True
    fov_radius: int = 10

    max_monsters_per_room: int = 3

    colors: dict = {
        "dark_wall": tcod.Color(0, 0, 100),
        "dark_ground": tcod.Color(50, 50, 150),
        "light_wall": tcod.Color(130, 110, 50),
        "light_ground": tcod.Color(200, 180, 50),
    }

    game_map: GameMap = GameMap(map_width, map_height)
    entities: List[Entity] = list()

    game_map.make_map(max_rooms, room_min_size, room_max_size)

    player_fighter_component = Fighter(30, 2, 5)
    player: Entity = Entity(
        int(screen_width / 2),
        int(screen_height / 2),
        "@",
        tcod.white,
        "player",
        RenderOrder.ACTOR,
        True,
        player_fighter_component
    )
    entities.append(player)

    player.x, player.y = game_map.rooms[0].center

    game_map.populate_map(entities, max_monsters_per_room)

    fov_recompute: bool = True
    fov_map: tcod.map.Map = initialize_fov(game_map)

    message_log: MessageLog = MessageLog(message_x, message_width, message_height)

    game_state: GameStates = GameStates.PLAYERS_TURN

    tilesheet = tcod.tileset.load_tilesheet(
        "Codepage-437.png", 32, 8, tcod.tileset.CHARMAP_CP437
    )

    mouse_coords: List[int] = [None, None]

    console = tcod.Console(screen_width, screen_height)
    panel = tcod.Console(screen_width, panel_height)

    with tcod.context.new_terminal(
        console.width, console.height, tileset=tilesheet, title="roguelike tutorial"
    ) as context:
        while True:
            console.clear()
            panel.clear()
            if fov_recompute:
                recompute_fov(fov_map, player.x, player.y,
                              fov_radius, fov_light_walls, fov_algorithm)
                fov_recompute = False
            # TODO We probably don't need to call render_terrain on every loop
            render_terrain(console, game_map, fov_map, colors)
            render_entities(console, entities, fov_map)
            render_player_stats(panel, bar_width, player)
            render_message_log(panel, message_log)
            panel.blit(console, 0, panel_y, 0, 0, screen_width, panel_height)
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

            player_turn_results = list()

            for event in tcod.event.wait():
                context.convert_event(event)
                if event.type == "QUIT":
                    raise SystemExit()
                if event.type == "KEYDOWN":
                    action: [Action, None] = handle_keys(event.sym)

                    if action is None:
                        continue

                    action_type: ActionType = action.action_type

                    if action_type == ActionType.MOVEMENT \
                       and game_state == GameStates.PLAYERS_TURN:
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
                    elif action_type == ActionType.ESCAPE:
                        raise SystemExit()
                if event.type == "MOUSEMOTION":
                    if event.tile.x < map_width and event.tile.y < map_height:
                        new_mouse_coords = [event.tile.x, event.tile.y]
                        if new_mouse_coords != mouse_coords:
                            mouse_coords = new_mouse_coords
                            if fov_map.fov[event.tile.x][event.tile.y]:
                                location_entities = get_entities_at(
                                    event.tile.x, event.tile.y, entities
                                )
                                if location_entities:
                                    msg = ', '.join(
                                        map(lambda e: e.name, location_entities)
                                    )
                                    message_log.add_message(
                                        Message(f"You see here: {msg}", tcod.gray)
                                    )

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


if __name__ == "__main__":
    main()
