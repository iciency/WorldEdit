from endstone_worldedit.utils import command_executor

command = {
    "pos2": {
        "description": "Sets the second position to the player's location.",
        "usage": "/pos2",
        "permissions": ["worldedit.command.pos"]
    }
}

@command_executor("pos2")
def handler(plugin, sender, args):
    player_uuid = sender.unique_id
    location = sender.location
    pos = (location.x, location.y, location.z)

    if player_uuid not in plugin.selections:
        plugin.selections[player_uuid] = {}
    
    plugin.selections[player_uuid]['pos2'] = pos
    sender.send_message(f"Position 2 set to {pos}.")
    return True
