from endstone_worldedit.utils import command_executor

command = {
    "undo": {
        "description": "Undoes the last action.",
        "usages": ["/undo"],
        "permissions": ["worldedit.command.undo"]
    }
}

@command_executor("undo")
def handler(plugin, sender, args):
    player_uuid = sender.unique_id
    if player_uuid not in plugin.undo_history or not plugin.undo_history[player_uuid]:
        sender.send_message("There is nothing to undo.")
        return False

    dimension = sender.dimension
    
    # Get the last action from undo history
    last_action = plugin.undo_history[player_uuid].pop()
    
    # Prepare redo entry
    redo_entry = []
    for x, y, z, _, _ in last_action:
        block = dimension.get_block_at(x, y, z)
        redo_entry.append((x, y, z, block.type, block.data))

    # Add to redo history
    if player_uuid not in plugin.redo_history:
        plugin.redo_history[player_uuid] = []
    plugin.redo_history[player_uuid].append(redo_entry)

    # Restore blocks
    for x, y, z, block_type, data_value in last_action:
        block = dimension.get_block_at(x, y, z)
        block.set_type(block_type)
        # if data_value is not None:
        #     # block.data = data_value # Endstone API is read-only
        #     pass

    sender.send_message("Last action undone.")
    return True
