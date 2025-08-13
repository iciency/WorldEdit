from endstone import Player

command = {
    "pos2": {
        "description": "Sets the second position to the player's location.",
        "usage": "/pos2",
        "permissions": ["worldedit.command.pos"]
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
    location = sender.location
    pos = (location.x, location.y, location.z)

    if player_uuid not in plugin.selections:
        plugin.selections[player_uuid] = {}
    
    plugin.selections[player_uuid]['pos2'] = pos
    sender.send_message(f"Position 2 set to {pos}.")
    return True
