import tcod

from typing import List
from game_messages import Message
from components.ai import ConfusedMonster


def heal(entity, **kwargs) -> List[dict]:
    results: List[dict] = list()

    amount: int = kwargs["amount"]

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({
            "consumed": False,
            "message": Message("You are already at full health.", tcod.yellow)
        })
    else:
        entity.fighter.heal(amount)
        results.append({
            "consumed": True,
            "message": Message("Your wounds start to feel better!", tcod.green)
        })

    return results


def cast_lightning(*args, **kwargs) -> List[dict]:
    caster = args[0]
    entities = kwargs["entities"]
    fov_map = kwargs["fov_map"]
    damage = kwargs["damage"]
    maximum_range = kwargs["maximum_range"]

    results: List[dict] = list()

    target = None
    closest_distance: int = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and fov_map.fov[entity.x][entity.y]:
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({
            "consumed": True,
            "target": target,
            "message": Message(
                (f"A lightning bolt strikes the {target.name} with a loud thunder,"
                 f" hitting it for {damage} damage!."), tcod.cyan
            )
        })
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({
            "consumed": False,
            "target": None,
            "message": Message("No enemy is close enough to strike.", tcod.red)
        })

    return results


def cast_fireball(entity, **kwargs) -> List[dict]:
    entities = kwargs["entities"]
    fov_map = kwargs["fov_map"]
    damage = kwargs["damage"]
    radius = kwargs["radius"]
    target_x = kwargs["target_x"]
    target_y = kwargs["target_y"]

    results: List[dict] = list()

    if not fov_map.fov[target_x][target_y]:
        results.append({
            "consumed": False,
            "message": Message(
                "You cannot target a tile outside your field of view.", tcod.red
            )
        })
    else:
        results.append({
            "consumed": True,
            "message": Message(
                f"The fireball explodes, burning everything with {radius} tiles!",
                tcod.orange
            )
        })

        for entity in entities:
            if entity.distance(target_x, target_y) <= radius and entity.fighter:
                results.append({
                    "message": Message(
                        f"The {entity.name} gets burned for {damage} hit points.",
                        tcod.orange
                    )
                })
                results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confusion(entity, **kwargs) -> List[dict]:
    entities = kwargs["entities"]
    fov_map = kwargs["fov_map"]
    target_x = kwargs["target_x"]
    target_y = kwargs["target_y"]

    results: List[dict] = list()

    if not fov_map.fov[target_x][target_y]:
        results.append({
            "consumed": False,
            "message": Message(
                "You cannot target a tile outside your field of view.", tcod.red
            )
        })
    else:
        for entity in entities:
            if entity.x == target_x and entity.y == target_y and entity.ai:
                confused_ai = ConfusedMonster(entity.ai, 10)
                confused_ai.owner = entity
                entity.ai = confused_ai

                results.append({
                    "consumed": True,
                    "message": Message(
                        (f"The eyes of the {entity.name} look vacant"
                         " as he starts to stumble around!"),
                        tcod.light_han
                    )
                })
                break
        else:
            results.append({
                "consumed": False,
                "message": Message(
                    "There is no targetable monster at that location.", tcod.yellow
                )
            })

    return results
