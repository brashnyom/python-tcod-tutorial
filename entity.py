from typing import List


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(
        self, x: int, y: int, char: str, color, name: str, blocks: bool = False
    ):
        self.x: int = x
        self.y: int = y
        self.char: str = char
        self.color = color
        self.name: str = name
        self.blocks: bool = blocks

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy


def get_blocking_entity_at(x: int, y: int, entities: List[Entity]):
    for entity in entities:
        if entity.x == x and entity.y == y and entity.blocks:
            return entity
    return None
