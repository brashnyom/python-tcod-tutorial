from typing import Any, List


class Fighter:
    def __init__(self, hp: int, defense: int, power: int):
        self.owner: Any = None
        self.max_hp: int = hp
        self.hp: int = hp
        self.defense: int = defense
        self.power: int = power

    def take_damage(self, amount: int) -> List[dict]:
        results: List[dict] = list()
        self.hp -= amount
        if self.hp <= 0:
            results.append({"dead": self.owner})
        return results

    def attack(self, target) -> List[dict]:
        results: List[dict] = list()
        # TODO Add type hint for Entity (target) without circular dependency
        damage: int = self.power - target.fighter.defense
        if damage > 0:
            results.append({
                "message": (f"{self.owner.name} attacks {target.name}"
                            f" for {damage} hit points.")
            })
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({
                "message": (f"{self.owner.name} attacks {target.name}"
                            " but does no damage.")
            })
        return results