import os
import nbtlib
from nbtlib.tag import *
from ..utils import command_executor, LEGACY_ID_TO_BEDROCK_NAME, translate_block_name

def read_varint(stream):
    result = 0
    shift = 0
    while True:
        byte = next(stream)
        result |= (byte & 0x7F) << shift
        if (byte & 0x80) == 0:
            break
        shift += 7
    return result

command = {
    "schem": {
        "description": "Manages schematics (Modern & Legacy).",
        "usages": [
            "/schem save <name: string>",
            "/schem load <name: string>",
            "/schem list"
        ],
        "permissions": ["worldedit.command.schem"]
    }
}

@command_executor("schem")
def handler(plugin, sender, args):
    if len(args) < 1:
        sender.send_message("Usage: /schem <save|load|list> [name]")
        return False

    sub_command = args[0].lower()
    schematic_path = plugin.plugin_config.get("schematic-path", "plugins/WorldEdit/schematics")

    if sub_command == "list":
        if not os.path.exists(schematic_path):
            sender.send_message("Schematic directory not found.")
            return False
        files = [f.replace('.schem', '') for f in os.listdir(schematic_path) if f.endswith('.schem')]
        if not files:
            sender.send_message("No schematics found.")
        else:
            sender.send_message("Available schematics: " + ", ".join(files))
        return True

    if sub_command == "save":
        if len(args) < 2:
            sender.send_message("Usage: /schem save <name>")
            return False
        
        name = args[1]
        player_uuid = sender.unique_id

        if player_uuid not in plugin.selections or 'pos1' not in plugin.selections[player_uuid] or 'pos2' not in plugin.selections[player_uuid]:
            sender.send_message("You must set both positions first.")
            return False

        pos1, pos2 = plugin.selections[player_uuid]['pos1'], plugin.selections[player_uuid]['pos2']
        dimension = sender.dimension
        
        min_x, max_x = min(pos1[0], pos2[0]), max(pos1[0], pos2[0])
        min_y, max_y = min(pos1[1], pos2[1]), max(pos1[1], pos2[1])
        min_z, max_z = min(pos1[2], pos2[2]), max(pos1[2], pos2[2])

        width, height, length = int(max_x - min_x + 1), int(max_y - min_y + 1), int(max_z - min_z + 1)
        
        # Create a palette by finding all unique block types in the selection
        all_blocks = [str(dimension.get_block_at(x, y, z).type) for y in range(min_y, max_y + 1) for z in range(min_z, max_z + 1) for x in range(min_x, max_x + 1)]
        palette_map = {name: i for i, name in enumerate(sorted(list(set(all_blocks))))}
        
        # Create BlockData array using palette indices
        block_data = bytearray(width * height * length)
        for i, block_name in enumerate(all_blocks):
            block_data[i] = palette_map[block_name]

        nbt_palette = nbtlib.Compound({name: nbtlib.Int(index) for name, index in palette_map.items()})

        schematic_nbt = nbtlib.File({
            'Schematic': nbtlib.Compound({
                'Width': nbtlib.Short(width), 'Height': nbtlib.Short(height), 'Length': nbtlib.Short(length),
                'Palette': nbt_palette,
                'BlockData': nbtlib.ByteArray(block_data),
                'Entities': nbtlib.List[nbtlib.Compound]([]),
                'TileEntities': nbtlib.List[nbtlib.Compound]([]),
            })
        })
        
        file_path = os.path.join(schematic_path, f"{name}.schem")
        schematic_nbt.save(file_path, gzipped=True)
        sender.send_message(f"Schematic '{name}.schem' saved in modern format.")
        return True

    elif sub_command == "load":
        if len(args) < 2:
            sender.send_message("Usage: /schem load <name>")
            return False
        
        name = args[1]
        file_path = os.path.join(schematic_path, f"{name}.schem")

        if not os.path.exists(file_path):
            sender.send_message(f"Schematic '{name}.schem' not found.")
            return False

        try:
            nbt_file = nbtlib.load(file_path, gzipped=True)
            schematic = nbt_file.get('Schematic', nbt_file) # Handle root tag being 'Schematic' or the data itself
        except Exception as e:
            sender.send_message(f"Error reading schematic file: {e}")
            return False

        if not all(k in schematic for k in ['Width', 'Height', 'Length']):
            sender.send_message("Invalid schematic: Missing Width, Height, or Length tags.")
            return False

        width, height, length = schematic['Width'], schematic['Height'], schematic['Length']
        blocks_to_change = []
        player_uuid, dimension, player_location = sender.unique_id, sender.dimension, sender.location

        # Modern schematics (Sponge v2 format with Palette)
        if 'Palette' in schematic and 'BlockData' in schematic:
            sender.send_message("Loading modern schematic (Palette)...")
            id_to_name = {v: k for k, v in schematic['Palette'].items()}
            block_data_stream = iter(schematic['BlockData'])
            
            for y in range(height):
                for z in range(length):
                    for x in range(width):
                        palette_index = read_varint(block_data_stream)
                        java_name = id_to_name.get(palette_index, "minecraft:air")
                        block_name, data_value = translate_block_name(plugin, java_name)
                        
                        if block_name != "minecraft:air":
                            # Ensure all coordinates are integers for precise placement
                            target_x = int(player_location.x) + x
                            target_y = int(player_location.y) + y
                            target_z = int(player_location.z) + z
                            blocks_to_change.append((target_x, target_y, target_z, block_name, data_value))
        # Legacy schematics (MCEdit format with numeric IDs)
        elif 'Blocks' in schematic:
            sender.send_message("Loading legacy schematic (Block IDs)...")
            block_ids = schematic['Blocks']
            
            for y in range(height):
                for z in range(length):
                    for x in range(width):
                        index = (y * length + z) * width + x
                        java_name = LEGACY_ID_TO_BEDROCK_NAME.get(str(block_ids[index]), "minecraft:air")
                        block_name, data_value = translate_block_name(plugin, java_name)

                        if block_name != "minecraft:air":
                            # Ensure all coordinates are integers for precise placement
                            target_x = int(player_location.x) + x
                            target_y = int(player_location.y) + y
                            target_z = int(player_location.z) + z
                            blocks_to_change.append((target_x, target_y, target_z, block_name, data_value))
        else:
            sender.send_message("Unsupported schematic format. Missing Palette/BlockData or Blocks tags.")
            return False

        if not blocks_to_change:
            sender.send_message("Schematic is empty or only contains air.")
            return True

        sender.send_message(f"Placing {len(blocks_to_change)} blocks...")

        # Define blocks that need a solid block underneath them
        dependent_blocks = [
            "flower", "sapling", "mushroom", "torch", "rail", "redstone_wire", "repeater", "comparator",
            "sign", "door", "lever", "button", "pressure_plate", "tripwire_hook", "tripwire", "banner"
        ]

        solid_pass = [b for b in blocks_to_change if not any(d in b[3] for d in dependent_blocks)]
        dependent_pass = [b for b in blocks_to_change if any(d in b[3] for d in dependent_blocks)]

        # Combine passes for undo history
        full_undo_entry = [(x, y, z, str(dimension.get_block_at(x, y, z).type), dimension.get_block_at(x, y, z).data) for x, y, z, _, _ in blocks_to_change]
        if player_uuid not in plugin.undo_history:
            plugin.undo_history[player_uuid] = []
        plugin.undo_history[player_uuid].append(full_undo_entry)
        plugin.redo_history[player_uuid] = []

        # Function to execute a pass
        def execute_pass(blocks_pass):
            if len(blocks_pass) > plugin.plugin_config["async-threshold"]:
                plugin.tasks[player_uuid] = {"dimension": dimension, "blocks": blocks_pass}
                sender.send_message(f"Starting async operation for {len(blocks_pass)} blocks...")
            else:
                for x, y, z, block_type, data_value in blocks_pass:
                    try:
                        block = dimension.get_block_at(x, y, z)
                        block.set_type(block_type)
                        # if data_value is not None:
                        #     # block.data = data_value # Endstone API is read-only
                        #     pass
                    except RuntimeError as e:
                        plugin.logger.error(f"Skipping block '{block_type}' for player {sender.name}: {e}")
                        sender.send_message(f"§cSkipped block: {block_type} ({e})§r")
                        continue

        # Execute passes
        execute_pass(solid_pass)
        execute_pass(dependent_pass)

        sender.send_message(f"Operation complete ({len(blocks_to_change)} blocks affected).")
        return True

    sender.send_message(f"Unknown sub-command '{sub_command}'. Use save, load, or list.")
    return False
