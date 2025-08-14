from endstone_worldedit.utils import command_executor

command = {
    "pos1": {
        "description": "Sets the first position to the player's location.",
        "usage": "/pos1",
        "permissions": ["worldedit.command.pos"]
    }
}

@command_executor("pos1")
def handler(plugin, sender, args):
    player_uuid = sender.unique_id
    location = sender.location
    pos = (location.x, location.y, location.z)

    if player_uuid not in plugin.selections:
        plugin.selections[player_uuid] = {}
    
    plugin.selections[player_uuid]['pos1'] = pos
    sender.send_message(f"Position 1 set to {pos}.")
    return True
