from endstone_worldedit.utils import command_executor

command = {
    "sel": {
        "description": "Manages the selection.",
        "usages": ["/sel <clear|toggle>"],
        "aliases": ["deselect"],
        "permissions": ["worldedit.command.sel"]
    }
}

@command_executor("sel")
def handler(plugin, sender, args):
    if not args:
        sender.send_message("Usage: /sel <clear|toggle>")
        return False

    sub_command = args[0].lower()
    player_uuid = sender.unique_id

    if sub_command == 'clear':
        if player_uuid in plugin.selections:
            del plugin.selections[player_uuid]
            sender.send_message("Selection cleared.")
        else:
            sender.send_message("You don't have a selection to clear.")
    elif sub_command == 'toggle':
        current_state = plugin.particle_toggle.get(player_uuid, True)
        plugin.particle_toggle[player_uuid] = not current_state
        new_state = "OFF" if current_state else "ON"
        sender.send_message(f"Selection particles turned {new_state}.")
    else:
        sender.send_message("Usage: /sel <clear|toggle>")
        return False
        
    return True
