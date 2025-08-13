from endstone import Player

command = {
    "undo": {
        "description": "Undoes the last action.",
        "usages": ["/undo"],
        "permissions": ["worldedit.command.undo"]
    }
}

def handler(plugin, sender, args):
    if not sender.is_op():
        sender.send_message("You do not have permission to use this command.")
        return False

    if not isinstance(sender, Player):
        sender.send_message("This command can only be used by a player.")
        return False

    player_uuid = sender.unique_id
    if player_uuid not in plugin.history or not plugin.history[player_uuid]:
        sender.send_message("There is nothing to undo.")
        return False

    dimension = sender.dimension
    for x, y, z, block_type in plugin.history[player_uuid]:
        block = dimension.get_block_at(x, y, z)
        block.set_type(block_type)

    plugin.history[player_uuid] = []  # Clear the history after undoing
    sender.send_message("Last action undone.")
    return True
