import math
from endstone_worldedit.utils import command_executor

command = {
    "cyl": {
        "description": "Creates a solid cylinder.",
        "usages": ["/cyl <block: block> <radius: int> [height: int]"],
        "permissions": ["worldedit.command.cylinder"]
    }
}

@command_executor("cyl")
def handler(plugin, sender, args):
    if len(args) < 2:
        sender.send_message("Usage: /cyl <block> <radius> [height]")
        return False

    block_name = args[0]
    try:
        radius = int(args[1])
        height = int(args[2]) if len(args) > 2 else 1
    except ValueError:
        sender.send_message("Radius and height must be integers.")
        return False

    player_uuid = sender.unique_id
    dimension = sender.dimension
    center = sender.location

    undo_entry = []
    plugin.redo_history[player_uuid] = []

    blocks_to_change = []
    for y in range(int(center.y), int(center.y) + height):
        for x in range(int(center.x) - radius, int(center.x) + radius + 1):
            for z in range(int(center.z) - radius, int(center.z) + radius + 1):
                if math.sqrt((x - center.x)**2 + (z - center.z)**2) <= radius:
                    blocks_to_change.append((x, y, z, block_name, None))

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
