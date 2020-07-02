from typing import Any


class Level:
    def __init__(
        self,
        current_level: int = 1,
        current_xp: int = 0,
        level_up_base: int = 200,
        level_up_factor: int = 150,
    ):
        self.owner: Any = None
        self.current_level: int = current_level
        self.current_xp: int = current_xp
        self.level_up_base: int = level_up_base
        self.level_up_factor: int = level_up_factor

    @property
    def experience_to_next_level(self) -> int:
        return self.level_up_base + self.current_level * self.level_up_factor

    def add_xp(self, xp: int) -> bool:
        self.current_xp += xp

        if self.current_xp > self.experience_to_next_level:
            self.current_xp -= self.experience_to_next_level
            self.current_level += 1
            return True
        else:
            return False
