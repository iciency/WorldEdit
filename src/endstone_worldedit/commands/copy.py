from endstone import Player

command = {
    "copy": {
        "description": "Copies the selection.",
        "usages": ["/copy"],
        "permissions": ["worldedit.command.copy"]
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
    if player_uuid not in plugin.selections or 'pos1' not in plugin.selections[player_uuid] or 'pos2' not in plugin.selections[player_uuid]:
        sender.send_message("You must set both positions first.")
        return False

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
