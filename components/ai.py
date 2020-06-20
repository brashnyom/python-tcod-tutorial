import tcod

from typing import Any, List


class BasicMonster:
    def __init__(self):
        self.owner: Any = None

    def take_turn(
        self,
        target,
        fov_map: tcod.map.Map,
        game_map,
        entities: list
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
