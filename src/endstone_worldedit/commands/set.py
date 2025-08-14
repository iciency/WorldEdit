from endstone import Player
from endstone.block import Block

command = {
    "set": {
        "description": "Fills the selection with a block.",
        "usages": ["/set <block: block>"],
        "permissions": ["worldedit.command.set"]
    }
}

def handler(plugin, sender, args):
    if not sender.is_op:
        sender.send_message("You do not have permission to use this command.")
        return False

    if not isinstance(sender, Player):
        sender.send_message("This command can only be used by a player.")
        return False

    if not args:
        sender.send_message("Usage: /set <block>")
        return False

    player_uuid = sender.unique_id
    if player_uuid not in plugin.selections or 'pos1' not in plugin.selections[player_uuid] or 'pos2' not in plugin.selections[player_uuid]:
        sender.send_message("You must set both positions first.")
        return False

    pos1 = plugin.selections[player_uuid]['pos1']
    pos2 = plugin.selections[player_uuid]['pos2']
    block_name = args[0]

    undo_entry = []
    plugin.redo_history[player_uuid] = []  # Clear redo history on new action
    dimension = sender.dimension
    min_x = min(pos1[0], pos2[0])
    max_x = max(pos1[0], pos2[0])
    min_y = min(pos1[1], pos2[1])
    max_y = max(pos1[1], pos2[1])
    min_z = min(pos1[2], pos2[2])
    max_z = max(pos1[2], pos2[2])

    for x in range(int(min_x), int(max_x) + 1):
        for y in range(int(min_y), int(max_y) + 1):
            for z in range(int(min_z), int(max_z) + 1):
                block = dimension.get_block_at(x, y, z)
                undo_entry.append((x, y, z, block.type))
                block.set_type(block_name)
    
    if player_uuid not in plugin.undo_history:
        plugin.undo_history[player_uuid] = []
    plugin.undo_history[player_uuid].append(undo_entry)
    sender.send_message("Area filled.")
    return True
