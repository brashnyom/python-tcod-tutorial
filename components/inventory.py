import tcod

from typing import List, Any
from game_messages import Message


class Inventory:
    def __init__(self, capacity: int):
        self.owner: Any = None
        self.capacity: int = capacity
        self.items: list = list()

    def add_item(self, item) -> List[dict]:
        results: List[dict] = list()

        if len(self.items) >= self.capacity:
            results.append({
                "item_added": None,
                "message": Message("Cannot pick up, inventory is full.", tcod.yellow)
            })
        else:
            results.append({
                "item_added": item,
                "message": Message(f"You pick up the {item.name}!", tcod.lighter_blue)
            })
            self.items.append(item)

        return results

    def remove_item(self, item):
        self.items.remove(item)

    def use(self, item_entity, **kwargs) -> List[dict]:
        results: List[dict] = list()

        item_component = item_entity.item
        if item_component.use_function is None:
            results.append({
                "message": Message(
                    f"The {item_entity.name} cannot be used.", tcod.yellow
                )
            })
        else:
            kwargs = {**item_component.function_kwargs, **kwargs}
            item_use_results = item_component.use_function(self.owner, **kwargs)
            for item_use_result in item_use_results:
                if item_use_result.get("consumed"):
                    self.remove_item(item_entity)
            results.extend(item_use_results)

        return results

    def drop(self, item_entity, **kwargs) -> List[dict]:
        results: List[dict] = list()
        results.append({
            "item_dropped": item_entity,
            "message": Message(
                f"You drop the {item_entity.name}.", tcod.yellow
            )
        })

        item_entity.x = self.owner.x
        item_entity.y = self.owner.y
        self.remove_item(item_entity)
        return results
