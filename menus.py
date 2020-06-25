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


def inventory_menu(con, header: str, inventory: Inventory, inventory_width: int):
    # show a menu with each item of the inventory as an option

    options: list
    if len(inventory.items) == 0:
        options = ["Inventory is empty."]
    else:
        options = [item.name for item in inventory.items]

    menu(con, header, options, inventory_width)
