import tcod

from actions import Action, ActionType
from input_handlers import handle_keys
from entity import Entity
from render_functions import render_all
from map_objects.game_map import GameMap


def main():
    screen_width: int = 80
    screen_height: int = 50

    map_width: int = 80
    map_height: int = 45

    colors = {
        "dark_wall": tcod.Color(0, 0, 100),
        "dark_ground": tcod.Color(50, 50, 150),
    }

    game_map = GameMap(map_width, map_height)

    player = Entity(int(screen_width / 2), int(screen_height / 2), "@", tcod.white)
    npc = Entity(int(screen_width / 2) - 5, int(screen_height / 2), "@", tcod.yellow)

    entities = [player, npc]

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

            render_all(root_console, game_map, entities, colors)

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
                    elif action_type == ActionType.ESCAPE:
                        raise SystemExit()


if __name__ == "__main__":
    main()
