from endstone_worldedit.utils import command_executor

command = {
    "overlay": {
        "description": "Drapes a layer of blocks over the selection.",
        "usages": ["/overlay <block: block>"],
        "permissions": ["worldedit.command.overlay"]
    }
}

@command_executor("overlay", selection_required=True)
def handler(plugin, sender, args):
    if len(args) < 1:
        sender.send_message("Usage: /overlay <block>")
        return False

    block_name = args[0]

    player_uuid = sender.unique_id
    pos1 = plugin.selections[player_uuid]['pos1']
    pos2 = plugin.selections[player_uuid]['pos2']
    
    dimension = sender.dimension
    
    undo_entry = []
    plugin.redo_history[player_uuid] = []

    blocks_to_change = []
    min_x, max_x = min(pos1[0], pos2[0]), max(pos1[0], pos2[0])
    min_y, max_y = min(pos1[1], pos2[1]), max(pos1[1], pos2[1])
    min_z, max_z = min(pos1[2], pos2[2]), max(pos1[2], pos2[2])

    for x in range(int(min_x), int(max_x) + 1):
        for z in range(int(min_z), int(max_z) + 1):
            for y in range(int(max_y), int(min_y) - 1, -1):  # Iterate downwards
                block = dimension.get_block_at(x, y, z)
                if block.type != "minecraft:air":
                    # Found the top non-air block, so place the overlay block above it
                    if y + 1 <= max_y: # Ensure we don't build outside the selection
                        target_block = dimension.get_block_at(x, y + 1, z)
                        # Only overlay if the block above is air, to avoid filling caves
                        if target_block.type == "minecraft:air":
                            blocks_to_change.append((x, y + 1, z, block_name, None))
                    break  # Move to the next (x, z) column

    affected_blocks = len(blocks_to_change)

    for x, y, z, _, _ in blocks_to_change:
        block = dimension.get_block_at(x, y, z)
        undo_entry.append((x, y, z, block.type, block.data))

    if player_uuid not in plugin.undo_history:
        plugin.undo_history[player_uuid] = []
    plugin.undo_history[player_uuid].append(undo_entry)

    if affected_blocks > plugin.plugin_config["async-threshold"]:
        plugin.tasks[player_uuid] = {"dimension": dimension, "blocks": blocks_to_change}
        sender.send_message(f"Starting async operation for {affected_blocks} blocks...")
    else:
        for x, y, z, block_type, data_value in blocks_to_change:
            block = dimension.get_block_at(x, y, z)
            block.set_type(block_type)
            if data_value is not None:
                block.data = data_value
        sender.send_message(f"Operation complete ({affected_blocks} blocks affected).")
        
    return True
