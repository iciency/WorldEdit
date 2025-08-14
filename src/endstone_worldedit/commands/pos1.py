from endstone import Player

command = {
    "pos1": {
        "description": "Sets the first position to the player's location.",
        "usage": "/pos1",
        "permissions": ["worldedit.command.pos"]
    }
}

def handler(plugin, sender, args):
    if not sender.is_op:
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
    
    plugin.selections[player_uuid]['pos1'] = pos
    sender.send_message(f"Position 1 set to {pos}.")
    return True
