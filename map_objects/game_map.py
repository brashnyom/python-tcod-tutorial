import tcod

from random import randint
from typing import List, Final

from map_objects.tile import Tile
from map_objects.rectangle import Rect
from entity import Entity
from components.fighter import Fighter
from components.ai import BasicMonster
from components.item import Item
from components.stairs import Stairs
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from item_functions import heal, cast_lightning, cast_fireball, cast_confusion
from render_functions import RenderOrder
from game_messages import Message

from random_utils import from_dungeon_level, random_choice_from_dict


class GameMap:

    monster_types: Final[dict] = {
        "orc": {
            "string": "o",
            "color": tcod.desaturated_green,
            "hp": 20,
            "defense": 0,
            "power": 4,
            "xp": 35,
        },
        "troll": {
            "string": "T",
            "color": tcod.darker_green,
            "hp": 30,
            "defense": 2,
            "power": 8,
            "xp": 100,
        }
    }

    monster_chances: dict = {
        "orc": 80,
        "troll": 20,
    }

    item_choices: dict = {
        "healing_potion": 70,
        "sword": 10,
        "shield": 10,
        "lightning_scroll": 10,
        "fireball_scroll": 10,
        "confusion_scroll": 10,
    }

    def __init__(self, width: int, height: int, dungeon_level: int = 1):
        self.width: int = width
        self.height: int = height
        self.tiles = self.initialize_tiles()
        self.rooms: List[Rect] = list()
        self.dungeon_level: int = dungeon_level

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
        self.create_h_tunnel(l_room.center[0], r_room.center[0], l_room.center[1])
        self.create_v_tunnel(l_room.center[1], r_room.center[1], r_room.center[0])

    def connect_rooms_v(self, l_room: Rect, r_room: Rect):
        self.create_v_tunnel(l_room.center[1], r_room.center[1], l_room.center[0])
        self.create_h_tunnel(l_room.center[0], r_room.center[0], r_room.center[1])

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
        self, room: Rect, entities: List[Entity],
        max_monsters_per_room: int,
        max_items_per_room: int,
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
                monster_name = random_choice_from_dict(self.monster_chances)
                monster = self.monster_types[monster_name]

                monster_fighter = Fighter(
                    monster["hp"], monster["defense"], monster["power"], monster["xp"]
                )
                entities.append(Entity(
                    x, y, monster["string"], monster["color"], monster_name,
                    RenderOrder.ACTOR, True,
                    monster_fighter,
                    BasicMonster(),
                ))
        # TODO FIXME Fix code duplication from above
        for i in range(0, randint(0, max_items_per_room)):
            item_choice = random_choice_from_dict(self.item_choices)

            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            occupied = any([
                entity.x == x and entity.y == y for entity in entities
            ])
            if not occupied:
                if item_choice == "healing_potion":
                    item_component = Item(use_function=heal, amount=40)
                    entities.append(Entity(
                        x, y, "!", tcod.violet, "Healing Potion",
                        render_order=RenderOrder.ITEM, item=item_component
                    ))
                elif item_choice == "fireball_scroll":
                    item_component = Item(
                        use_function=cast_fireball,
                        damage=25,
                        radius=3,
                        targeting=True,
                        targeting_message=Message(
                            "Select a target and (f)ire.", tcod.light_cyan
                        )
                    )
                    entities.append(Entity(
                        x, y, "#", tcod.red, "Scroll of Fireball",
                        render_order=RenderOrder.ITEM, item=item_component
                    ))
                elif item_choice == "confusion_scroll":
                    item_component = Item(
                        use_function=cast_confusion,
                        targeting=True,
                        targeting_message=Message(
                            "Select a target and (f)ire.", tcod.light_cyan
                        )
                    )
                    entities.append(Entity(
                        x, y, "#", tcod.light_pink, "Scroll of Confusion",
                        render_order=RenderOrder.ITEM, item=item_component
                    ))
                elif item_choice == "sword":
                    equippable_component = Equippable(
                        EquipmentSlots.MAIN_HAND, power_bonus=3
                    )
                    entities.append(Entity(
                        x, y, "/", tcod.sky, "Sword",
                        render_order=RenderOrder.ITEM, equippable=equippable_component
                    ))
                elif item_choice == "shield":
                    equippable_component = Equippable(
                        EquipmentSlots.OFF_HAND, defense_bonus=1
                    )
                    entities.append(Entity(
                        x, y, "[", tcod.darker_orange, "Shield",
                        render_order=RenderOrder.ITEM, equippable=equippable_component
                    ))
                else:
                    item_component = Item(
                        use_function=cast_lightning, damage=40, maximum_range=5
                    )
                    entities.append(Entity(
                        x, y, "#", tcod.yellow, "Lightning Bolt Scroll",
                        render_order=RenderOrder.ITEM, item=item_component
                    ))

    def populate_map(self, entities: List[Entity]):
        max_monsters_per_room: int = from_dungeon_level(
                [[2, 1], [3, 4], [5, 6]], self.dungeon_level
        )
        max_items_per_room: int = from_dungeon_level(
                [[1, 1], [2, 4]], self.dungeon_level
        )

        self.monster_chances = {
            "orc": 80,
            "troll": from_dungeon_level(
                [[15, 3], [30, 5], [60, 7]], self.dungeon_level
            )
        }

        self.item_chances = {
            "healing_potion": 35,
            "sword": from_dungeon_level([[5, 4]], self.dungeon_level),
            "shield": from_dungeon_level([[15, 8]], self.dungeon_level),
            "lightning_scroll": from_dungeon_level([[25, 4]], self.dungeon_level),
            "fireball_scroll": from_dungeon_level([[25, 6]], self.dungeon_level),
            "confusion_scroll": from_dungeon_level([[10, 2]], self.dungeon_level),
        }

        for room in self.rooms:
            self.populate_room(
                room, entities, max_monsters_per_room, max_items_per_room
            )

        stairs_component = Stairs(self.dungeon_level + 1)
        x, y = self.rooms[-1].center
        down_stairs = Entity(
            x, y, ">", tcod.white, "Stairs",
            RenderOrder.STAIRS, stairs=stairs_component
        )
        entities.append(down_stairs)

    def is_blocked(self, x: int, y: int):
        return self.tiles[x][y].blocked

    def next_floor(self, player: Entity, message_log, config: dict):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(
            config["max_rooms"], config["room_min_size"], config["room_max_size"]
        )
        self.populate_map(entities)

        player.x, player.y = self.rooms[0].center
        player.fighter.heal(int(player.fighter.max_hp / 2))  # type: ignore
        message_log.add_message(Message(
            "You take a moment to rest, and recover your strength.", tcod.light_violet
        ))

        return entities
