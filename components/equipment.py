from typing import Any, List
from equipment_slots import EquipmentSlots


class Equipment:
    def __init__(self, main_hand=None, off_hand=None):
        self.owner: Any = None
        self.main_hand = main_hand
        self.off_hand = off_hand

    def _get_equipment_bonus(self, stat: str) -> int:
        bonus = 0

        if self.main_hand and self.main_hand.equippable:
            bonus += getattr(self.main_hand.equippable, stat)

        if self.off_hand and self.off_hand.equippable:
            bonus += getattr(self.off_hand.equippable, stat)

        return bonus

    @property
    def max_hp_bonus(self) -> int:
        return self._get_equipment_bonus("max_hp_bonus")

    @property
    def power_bonus(self) -> int:
        return self._get_equipment_bonus("power_bonus")

    @property
    def defense_bonus(self) -> int:
        return self._get_equipment_bonus("defense_bonus")

    def _toggle_equip_slot(self, hand_type: str, equippable_entity) -> List[dict]:
        results = list()
        hand = getattr(self, hand_type)

        if hand == equippable_entity:
            setattr(self, hand_type, None)
            results.append({"dequipped": equippable_entity})
        else:
            if hand:
                results.append({"dequipped": hand})
            setattr(self, hand_type, equippable_entity)
            results.append({"equipped": equippable_entity})
        return results

    def toggle_equip(self, equippable_entity) -> List[dict]:
        results = list()

        slot = equippable_entity.equippable.slot

        if slot == EquipmentSlots.MAIN_HAND:
            results = self._toggle_equip_slot("main_hand", equippable_entity)
        elif slot == EquipmentSlots.OFF_HAND:
            results = self._toggle_equip_slot("off_hand", equippable_entity)

        return results
