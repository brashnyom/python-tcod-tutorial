import tcod

from map_objects.game_map import GameMap


def initialize_fov(game_map: GameMap) -> tcod.map.Map:
    fov_map = tcod.map.Map(game_map.width, game_map.height, order="F")
    for x in range(0, game_map.width):
        for y in range(0, game_map.height):
            fov_map.transparent[x][y] = not game_map.tiles[x][y].block_sight
            fov_map.walkable[x][y] = game_map.tiles[x][y].blocked
    return fov_map


def recompute_fov(
    fov_map: tcod.map.Map,
    x: int,
    y: int,
    radius: int,
    light_walls: bool = True,
    algorithm: int = 0
):
    fov_map.compute_fov(x, y, radius, light_walls, algorithm)
