import tcod

from components.inventory import Inventory


def menu(con, header: str, options: list, width: int):
    if len(options) > 26:
        raise ValueError("Cannot have a menu with more than 26 options.")

    # calculate total height for the header + one line per option
    header_height: int = con.get_height_rect(
        0, 0, width, con.height, header
    )
    height: int = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = tcod.Console(width, height)

    # print the header
    window.print_box(0, 0, width, height, header, (255, 255, 255), alignment=tcod.LEFT)

    # print all the options
    y: int = header_height
    letter_index: int = ord("a")
    for option_text in options:
        text: str = f"({chr(letter_index)}) {option_text}"
        window.print(0, y, text, (255, 255, 255), alignment=tcod.LEFT)
        y += 1
        letter_index += 1

    # blit the contents of the window to the console
    x: int = int(con.width / 2 - width / 2)
    y = int(con.height / 2 - height / 2)
    window.blit(con, x, y, 0, 0, width, height)
    del(window)


def inventory_menu(con, header: str, player, inventory_width: int):
    # show a menu with each item of the inventory as an option
    inventory: Inventory = player.inventory

    options: list
    if len(inventory.items) == 0:
        options = ["Inventory is empty."]
    else:
        options = []
        for item in inventory.items:
            if player.equipment.main_hand == item:
                options.append(f"{item.name} (on main hand)")
            elif player.equipment.off_hand == item:
                options.append(f"{item.name} (on off hand)")
            else:
                options.append(item.name)

    menu(con, header, options, inventory_width)


def main_menu(con, background_image):
    background_image.blit_2x(con, 0, 0)
    con.print(
        int(con.width / 2),
        int(con.height / 2) - 4,
        "TOMBS OF THE ANCIENT KINGS",
        tcod.light_yellow,
        alignment=tcod.CENTER
    )
    con.print(
        int(con.width / 2),
        int(con.height - 2),
        "By brashnyom",
        tcod.light_yellow,
        alignment=tcod.CENTER
    )
    menu(con, "", ["Play a new game", "Continue last game", "Quit"], 24)


def message_box(console, header, width):
    menu(console, header, [], width)


def level_up_menu(console, header, player, menu_width):
    options = [
        f"Constitution (+20 HP, from {player.fighter.max_hp})",
        f"Strength (+1 attack, from {player.fighter.power})",
        f"Agility (+1 defense, from {player.fighter.defense})",
    ]
    menu(console, header, options, menu_width)


def character_screen(console, player, width: int, height: int):
    window = tcod.Console(width, height)

    stats = [
            f"Level: {player.level.current_level}",
            f"Experience: {player.level.current_xp}",
            f"Experience to next level: {player.level.experience_to_next_level}",
            f"Maximum HP: {player.fighter.max_hp}",
            f"Attack: {player.fighter.power}",
            f"Defense: {player.fighter.defense}",
    ]

    for pos, string in enumerate(stats):
        window.print_box(
            0, pos + 1, width, height, string, (255, 255, 255), alignment=tcod.LEFT
        )

    x: int = int(console.width / 2 - width / 2)
    y: int = int(console.height / 2 - height / 2)
    window.blit(console, x, y, 0, 0, width, height)
    del(window)
