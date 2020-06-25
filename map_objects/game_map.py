import tcod

from random import randint
from typing import List, Final

from map_objects.tile import Tile
from map_objects.rectangle import Rect
from entity import Entity
from components.fighter import Fighter
from components.ai import BasicMonster
from components.item import Item
from item_functions import heal
from render_functions import RenderOrder


class GameMap:

    monster_types: Final[dict] = {
        "orc": {
            "string": "o",
            "color": tcod.desaturated_green,
            "hp": 10,
            "defense": 0,
            "power": 3,
        },
        "troll": {
            "string": "T",
            "color": tcod.darker_green,
            "hp": 16,
            "defense": 1,
            "power": 4,
        }
    }

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.rooms: List[Rect] = list()

    def initialize_tiles(self):
        tiles = [
            [Tile(True) for g in range(0, self.height)]
            for i in range(0, self.width)
        ]
        return tiles

    def carve_tile(self, x: int, y: int):
        self.tiles[x][y].blocked = False
        self.tiles[x][y].block_sight = False

    def create_room(self, room: Rect):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.carve_tile(x, y)

    def create_h_tunnel(self, x1: int, x2: int, y: int):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.carve_tile(x, y)

    def create_v_tunnel(self, y1: int, y2: int, x: int):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.carve_tile(x, y)

    def connect_rooms_h(self, l_room: Rect, r_room: Rect):
        self.create_h_tunnel(l_room.center.x, r_room.center.x, l_room.center.y)
        self.create_v_tunnel(l_room.center.y, r_room.center.y, r_room.center.x)

    def connect_rooms_v(self, l_room: Rect, r_room: Rect):
        self.create_v_tunnel(l_room.center.y, r_room.center.y, l_room.center.x)
        self.create_h_tunnel(l_room.center.x, r_room.center.x, r_room.center.y)

    def make_map(self, max_rooms: int, room_min_size: int, room_max_size: int):
        self.rooms = list()

        # randomly create max_rooms amount of rooms
        for i in range(0, max_rooms):
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            x = randint(0, self.width - (w + 1))
            y = randint(0, self.height - (h + 1))

            new_room = Rect(x, y, w, h)

            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    # TODO FIXME This does not allow us an exact choice
                    # of how many rooms we wish to have
                    break
            else:
                self.rooms.append(new_room)
                self.create_room(new_room)

        # connect each room to the next one (that's why we slice up to the last room)
        for room_index in range(0, len(self.rooms) - 1):
            # randomly choose initial direction of tunnel
            horizontal = bool(randint(0, 1))

            if horizontal:
                self.connect_rooms_h(self.rooms[room_index], self.rooms[room_index + 1])
            else:
                self.connect_rooms_v(self.rooms[room_index], self.rooms[room_index + 1])

    def populate_room(
        self, room: Rect, entities: List[Entity], max_monsters_per_room: int,
        max_items_per_room: int
    ):
        for i in range(0, randint(0, max_monsters_per_room)):
            x: int = randint(room.x1 + 1, room.x2 - 1)
            y: int = randint(room.y1 + 1, room.y2 - 1)
            occupied: bool = any([
                entity.x == x and entity.y == y for entity in entities
            ])
            if not occupied:
                # TODO FIXME Again, this does not allow us an exact choice
                # of how many monsters we want
                monster_type: int = randint(0, 100)
                if monster_type < 80:
                    monster_name = "orc"
                else:
                    monster_name = "troll"
                monster = self.monster_types[monster_name]
                entities.append(Entity(
                    x, y, monster["string"], monster["color"], monster_name,
                    RenderOrder.ACTOR, True,
                    Fighter(monster["hp"], monster["defense"], monster["power"]),
                    BasicMonster()
                ))
        # TODO FIXME Fix code duplication from above
        for i in range(0, randint(0, max_items_per_room)):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            occupied = any([
                entity.x == x and entity.y == y for entity in entities
            ])
            if not occupied:
                item_component = Item(use_function=heal, amount=4)
                entities.append(Entity(
                    x, y, "!", tcod.violet, "Healing Potion",
                    render_order=RenderOrder.ITEM, item=item_component
                ))

    def populate_map(
        self, entities: List[Entity], max_monsters_per_room: int,
        max_items_per_room: int
    ):
        for room in self.rooms:
            self.populate_room(
                room, entities, max_monsters_per_room, max_items_per_room
            )

    def is_blocked(self, x: int, y: int):
        return self.tiles[x][y].blocked
