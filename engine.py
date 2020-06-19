import tcod

from typing import List

from actions import Action, ActionType
from input_handlers import handle_keys
from entity import Entity
from render_functions import render_terrain, render_entities
from fov_functions import initialize_fov, recompute_fov
from map_objects.game_map import GameMap


def main():
    screen_width: int = 80
    screen_height: int = 50

    map_width: int = 80
    map_height: int = 45

    room_max_size: int = 10
    room_min_size: int = 6
    max_rooms: int = 30

    fov_algorithm: int = 0
    fov_light_walls: bool = True
    fov_radius: int = 10

    colors: dict = {
        "dark_wall": tcod.Color(0, 0, 100),
        "dark_ground": tcod.Color(50, 50, 150),
        "light_wall": tcod.Color(130, 110, 50),
        "light_ground": tcod.Color(200, 180, 50),
    }

    game_map: GameMap = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size)

    player = Entity(int(screen_width / 2), int(screen_height / 2), "@", tcod.white)
    npc = Entity(int(screen_width / 2) - 5, int(screen_height / 2), "@", tcod.yellow)

    fov_recompute: bool = True

    fov_map: tcod.map.Map = initialize_fov(game_map)

    player.x, player.y = game_map.rooms[0].center
    npc.x, npc.y = game_map.rooms[-1].center

    entities: List[Entity] = [player, npc]

    tcod.console_set_custom_font(
        "arial10x10.png",
        tcod.FONT_TYPE_GRAYSCALE | tcod.FONT_LAYOUT_TCOD
    )

    with tcod.console_init_root(
        w=screen_width,
        h=screen_height,
        title="libtcod tutorial",
        order="F",
        vsync=False
    ) as root_console:
        while True:

            root_console.clear()
            if fov_recompute:
                recompute_fov(fov_map, player.x, player.y,
                              fov_radius, fov_light_walls, fov_algorithm)
                fov_recompute = False
            # TODO We probably don't need to call render_terrain on every loop
            render_terrain(root_console, game_map, fov_map, colors)
            render_entities(root_console, entities, fov_map)
            tcod.console_flush()

            for event in tcod.event.wait():
                if event.type == "QUIT":
                    raise SystemExit()
                if event.type == "KEYDOWN":
                    action: [Action, None] = handle_keys(event.sym)

                    if action is None:
                        continue

                    action_type: ActionType = action.action_type

                    if action_type == ActionType.MOVEMENT:
                        dx: int = action.kwargs.get("dx", 0)
                        dy: int = action.kwargs.get("dy", 0)
                        if not game_map.is_blocked(player.x + dx, player.y + dy):
                            player.move(dx, dy)
                            fov_recompute = True
                    elif action_type == ActionType.ESCAPE:
                        raise SystemExit()


if __name__ == "__main__":
    main()
