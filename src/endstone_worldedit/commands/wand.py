from endstone import Player
from endstone.inventory import ItemStack

command = {
    "wand": {
        "description": "Gives the user the wand tool.",
        "usage": "/wand",
        "aliases": ["w"],
        "permissions": ["worldedit.command.wand"]
    }
}

def handler(plugin, sender, args):
    if not sender.is_op():
        sender.send_message("You do not have permission to use this command.")
        return False

    if not isinstance(sender, Player):
        sender.send_message("This command can only be used by a player.")
        return False
    
    sender.inventory.add_item(ItemStack("minecraft:wooden_axe"))
    sender.send_message("You have been given the wand tool.")
    return True
