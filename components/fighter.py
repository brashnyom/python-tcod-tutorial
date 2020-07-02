import tcod
from typing import Any, List

from game_messages import Message


class Fighter:
    def __init__(self, hp: int, defense: int, power: int, xp: int = 0):
        self.owner: Any = None
        self.max_hp: int = hp
        self.hp: int = hp
        self.defense: int = defense
        self.power: int = power
        self.xp: int = xp

    def take_damage(self, amount: int) -> List[dict]:
        results: List[dict] = list()
        self.hp -= amount
        if self.hp <= 0:
            results.append({"dead": self.owner, "xp": self.xp})
        return results

    def attack(self, target) -> List[dict]:
        results: List[dict] = list()
        # TODO Add type hint for Entity (target) without circular dependency
        damage: int = self.power - target.fighter.defense
        if damage > 0:
            message_text = (f"{self.owner.name} attacks {target.name}"
                            f" for {damage} hit points.")
            results.extend(target.fighter.take_damage(damage))
        else:
            message_text = (f"{self.owner.name} attacks {target.name}"
                            " but does no damage.")
        results.append({"message": Message(message_text, tcod.white)})
        return results

    def heal(self, amount: int):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
