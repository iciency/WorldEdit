from endstone import Player

command = {
    "paste": {
        "description": "Pastes the copied selection.",
        "usages": ["/paste"],
        "permissions": ["worldedit.command.paste"]
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
    if player_uuid not in plugin.clipboard or not plugin.clipboard[player_uuid]:
        sender.send_message("There is nothing to paste. Use /copy first.")
        return False

    dimension = sender.dimension
    player_location = sender.location
    
    undo_entry = []
    plugin.redo_history[player_uuid] = []  # Clear redo history on new action

    copied_blocks = plugin.clipboard[player_uuid]
    for relative_x, relative_y, relative_z, block_type in copied_blocks:
        target_x = int(player_location.x + relative_x)
        target_y = int(player_location.y + relative_y)
        target_z = int(player_location.z + relative_z)
        
        block = dimension.get_block_at(target_x, target_y, target_z)
        undo_entry.append((target_x, target_y, target_z, block.type))
        block.set_type(block_type)

    if player_uuid not in plugin.undo_history:
        plugin.undo_history[player_uuid] = []
    plugin.undo_history[player_uuid].append(undo_entry)
    
    sender.send_message(f"{len(copied_blocks)} blocks pasted.")
    return True
