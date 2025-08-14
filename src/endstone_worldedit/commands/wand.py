from endstone.inventory import ItemStack
from endstone_worldedit.utils import command_executor

command = {
    "wand": {
        "description": "Gives the user the wand tool.",
        "usage": "/wand",
        "aliases": ["w"],
        "permissions": ["worldedit.command.wand"]
    }
}

@command_executor("wand")
def handler(plugin, sender, args):
    sender.inventory.add_item(ItemStack("minecraft:wooden_axe"))
    sender.send_message("You have been given the wand tool.")
    return True
