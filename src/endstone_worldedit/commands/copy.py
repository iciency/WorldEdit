from endstone_worldedit.utils import command_executor

command = {
    "copy": {
        "description": "Copies the selection.",
        "usages": ["/copy"],
        "permissions": ["worldedit.command.copy"]
    }
}

@command_executor("copy", selection_required=True)
def handler(plugin, sender, args):
    player_uuid = sender.unique_id
    pos1 = plugin.selections[player_uuid]['pos1']
    pos2 = plugin.selections[player_uuid]['pos2']
    
    dimension = sender.dimension
    player_location = sender.location
    
    min_x = min(pos1[0], pos2[0])
    max_x = max(pos1[0], pos2[0])
    min_y = min(pos1[1], pos2[1])
    max_y = max(pos1[1], pos2[1])
    min_z = min(pos1[2], pos2[2])
    max_z = max(pos1[2], pos2[2])

    blocks = []
    for x in range(int(min_x), int(max_x) + 1):
        for y in range(int(min_y), int(max_y) + 1):
            for z in range(int(min_z), int(max_z) + 1):
                block = dimension.get_block_at(x, y, z)
                relative_x = x - player_location.x
                relative_y = y - player_location.y
                relative_z = z - player_location.z
                blocks.append((relative_x, relative_y, relative_z, block.type))

    plugin.clipboard[player_uuid] = blocks
    sender.send_message(f"{len(blocks)} blocks copied.")
    return True
