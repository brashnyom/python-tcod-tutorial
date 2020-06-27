import math
import numpy as np
import tcod

from typing import List, Optional
from components.fighter import Fighter
from components.ai import BasicMonster
from components.inventory import Inventory
from components.item import Item


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color,
        name: str,
        render_order,
        blocks: bool = False,
        fighter: Optional[Fighter] = None,
        ai: Optional[BasicMonster] = None,
        inventory: Optional[Inventory] = None,
        item: Optional[Item] = None,
    ):
        # TODO Add typing hints for RenderOrder without circular dependency
        self.x: int = x
        self.y: int = y
        self.char: str = char
        self.color = color
        self.name: str = name
        self.render_order = render_order
        self.blocks: bool = blocks
        self.fighter: Optional[Fighter] = fighter
        self.ai: Optional[BasicMonster] = ai
        self.inventory: Optional[Inventory] = inventory
        self.item: Optional[Item] = item

        if self.fighter:
            self.fighter.owner = self
        if self.ai:
            self.ai.owner = self
        if self.inventory:
            self.inventory.owner = self
        if self.item:
            self.item.owner = self

    def distance(self, x: int, y: int) -> float:
        dx: int = x - self.x
        dy: int = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance_to(self, other: "Entity") -> float:
        return self.distance(other.x, other.y)

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

    def move_towards(
        self, target_x: int, target_y: int, game_map, entities: List["Entity"]
    ):
        # TODO Add type hint for GameMap without circular dependency
        dx: int = target_x - self.x
        dy: int = target_y - self.y
        distance: float = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        new_x: int = self.x + dx
        new_y: int = self.y + dy

        blocking_entity = get_blocking_entity_at(new_x, new_y, entities)
        if not game_map.is_blocked(new_x, new_y) and blocking_entity is None:
            self.move(dx, dy)

    def move_astar(
        self, target: "Entity", game_map, entities: List["Entity"]
    ):
        # TODO This can be optimized, no need to be recalculated every time
        astar_map = np.array([
            [int(not game_map.tiles[x][y].blocked) for y in range(0, game_map.height)]
            for x in range(0, game_map.width)],
            dtype=np.int8
        )

        for entity in entities:
            if entity is target or entity is self or not entity.blocks:
                continue
            astar_map[entity.x][entity.y] = 0

        astar = tcod.path.AStar(astar_map)
        astar_path = astar.get_path(self.x, self.y, target.x, target.y)
        if astar_path:
            dx = astar_path[0][0] - self.x
            dy = astar_path[0][1] - self.y
            self.move(dx, dy)
        else:
            self.move_towards(target.x, target.y, game_map, entities)


def get_blocking_entity_at(x: int, y: int, entities: List[Entity]) -> Optional[Entity]:
    for entity in entities:
        if entity.x == x and entity.y == y and entity.blocks:
            return entity
    return None


def get_entities_at(x: int, y: int, entities: List[Entity]) -> List[Entity]:
    return [entity for entity in entities if entity.x == x and entity.y == y]
