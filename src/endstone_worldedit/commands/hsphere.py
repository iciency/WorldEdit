import math
from endstone_worldedit.utils import command_executor

command = {
    "hsphere": {
        "description": "Creates a hollow sphere.",
        "usages": ["/hsphere <block: block> <radius: int>"],
        "permissions": ["worldedit.command.sphere"]
    }
}

@command_executor("hsphere")
def handler(plugin, sender, args):
    if len(args) < 2:
        sender.send_message("Usage: /hsphere <block> <radius>")
        return False

    block_name = args[0]
    try:
        radius = int(args[1])
    except ValueError:
        sender.send_message("Radius must be an integer.")
        return False

    player_uuid = sender.unique_id
    dimension = sender.dimension
    center = sender.location

    undo_entry = []
    plugin.redo_history[player_uuid] = []

    blocks_to_change = []
    for x in range(int(center.x) - radius, int(center.x) + radius + 1):
        for y in range(int(center.y) - radius, int(center.y) + radius + 1):
            for z in range(int(center.z) - radius, int(center.z) + radius + 1):
                distance = math.sqrt((x - center.x)**2 + (y - center.y)**2 + (z - center.z)**2)
                if radius - 1 < distance <= radius:
                    blocks_to_change.append((x, y, z, block_name))

    affected_blocks = len(blocks_to_change)

    for x, y, z, _ in blocks_to_change:
        block = dimension.get_block_at(x, y, z)
        undo_entry.append((x, y, z, block.type))

    if player_uuid not in plugin.undo_history:
        plugin.undo_history[player_uuid] = []
    plugin.undo_history[player_uuid].append(undo_entry)

    if affected_blocks > plugin.plugin_config["async-threshold"]:
        plugin.tasks[player_uuid] = {"dimension": dimension, "blocks": blocks_to_change}
        sender.send_message(f"Starting async operation for {affected_blocks} blocks...")
    else:
        for x, y, z, type in blocks_to_change:
            block = dimension.get_block_at(x, y, z)
            block.set_type(type)
        sender.send_message(f"Operation complete ({affected_blocks} blocks affected).")
        
    return True
