from endstone_worldedit.utils import command_executor

command = {
    "walls": {
        "description": "Creates walls around the selection.",
        "usages": ["/walls <block: block>"],
        "permissions": ["worldedit.command.walls"]
    }
}

@command_executor("walls", selection_required=True)
def handler(plugin, sender, args):
    if len(args) < 1:
        sender.send_message("Usage: /walls <block>")
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

    for y in range(int(min_y), int(max_y) + 1):
        for x in range(int(min_x), int(max_x) + 1):
            blocks_to_change.append((x, y, min_z, block_name, None))
            blocks_to_change.append((x, y, max_z, block_name, None))
        for z in range(int(min_z) + 1, int(max_z)):
            blocks_to_change.append((min_x, y, z, block_name, None))
            blocks_to_change.append((max_x, y, z, block_name, None))

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
