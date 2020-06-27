import tcod

from random import randint
from typing import Any, List

from game_messages import Message


class BasicMonster:
    def __init__(self):
        self.owner: Any = None

    def take_turn(
        self, target, fov_map: tcod.map.Map, game_map, entities: list
    ) -> List[dict]:
        results: List[dict] = list()
        # TODO Add type hints for Entity and GameMap without circular dependency
        monster = self.owner

        # TODO The monster will chase only if the player sees it
        # This will probably need to be changed eventually
        if fov_map.fov[monster.x][monster.y]:
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, game_map, entities)
            elif target.fighter.hp > 0:
                results.extend(monster.fighter.attack(target))

        return results


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.owner: Any = None
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(
        self, target, fov_map: tcod.map.Map, game_map, entities: list
    ) -> List[dict]:
        results: List[dict] = list()

        if self.number_of_turns > 0:
            random_x: int = self.owner.x + randint(0, 2) - 1
            random_y: int = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x or random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({
                "message": Message(
                    f"The {self.owner.name} is no longer confused!", tcod.red
                )
            })
        return results
