from typing import Any


class Equippable:
    def __init__(
        self, slot, power_bonus: int = 0, defense_bonus: int = 0, max_hp_bonus: int = 0
    ):
        self.owner: Any = None
        self.slot = slot
        self.power_bonus: int = power_bonus
        self.defense_bonus: int = defense_bonus
        self.max_hp_bonus: int = max_hp_bonus
