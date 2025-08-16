from endstone_worldedit.utils import command_executor

command = {
    "paste": {
        "description": "Pastes the copied selection.",
        "usages": ["/paste"],
        "permissions": ["worldedit.command.paste"]
    }
}

@command_executor("paste")
def handler(plugin, sender, args):
    player_uuid = sender.unique_id
    if player_uuid not in plugin.clipboard or not plugin.clipboard[player_uuid]:
        sender.send_message("There is nothing to paste. Use /copy first.")
        return False

    dimension = sender.dimension
    player_location = sender.location
    
    undo_entry = []
    plugin.redo_history[player_uuid] = []  # Clear redo history on new action

    blocks_to_change = []
    copied_blocks = plugin.clipboard[player_uuid]
    for relative_x, relative_y, relative_z, block_type, data_value in copied_blocks:
        target_x = int(player_location.x + relative_x)
        target_y = int(player_location.y + relative_y)
        target_z = int(player_location.z + relative_z)
        blocks_to_change.append((target_x, target_y, target_z, block_type, data_value))

    affected_blocks = len(blocks_to_change)

    # Store undo history first
    for x, y, z, _, _ in blocks_to_change:
        block = dimension.get_block_at(x, y, z)
        undo_entry.append((x, y, z, block.type, block.data))

    if player_uuid not in plugin.undo_history:
        plugin.undo_history[player_uuid] = []
    plugin.undo_history[player_uuid].append(undo_entry)

    # Execute asynchronously if the task is large
    if affected_blocks > plugin.plugin_config["async-threshold"]:
        plugin.tasks[player_uuid] = {"dimension": dimension, "blocks": blocks_to_change}
        sender.send_message(f"Starting async operation for {affected_blocks} blocks...")
    else:
        for x, y, z, block_type, data_value in blocks_to_change:
            block = dimension.get_block_at(x, y, z)
            block.set_type(block_type)
            # if data_value is not None:
            #     # block.data = data_value # Endstone API is read-only
            #     pass
        sender.send_message(f"Operation complete ({affected_blocks} blocks affected).")
    return True
