import os
import nbtlib
from nbtlib.tag import *
from ..utils import command_executor, BEDROCK_TO_LEGACY_ID, LEGACY_ID_TO_BEDROCK_NAME

command = {
    "schem": {
        "description": "Manages schematics.",
        "usages": ["/schem <save|load|list> <name : string>"],
        "permissions": ["worldedit.command.schem"]
    }
}

@command_executor("schem")
def handler(plugin, sender, args):
    if len(args) < 1:
        sender.send_message("Usage: /schem <save|load|list> [name]")
        return False

    sub_command = args[0].lower()

    if sub_command == "save":
        if len(args) < 2:
            sender.send_message("Usage: /schem save <name>")
            return False
        
        name = args[1]
        player_uuid = sender.unique_id

        if player_uuid not in plugin.selections or 'pos1' not in plugin.selections[player_uuid] or 'pos2' not in plugin.selections[player_uuid]:
            sender.send_message("You must set both positions first.")
            return False

        pos1 = plugin.selections[player_uuid]['pos1']
        pos2 = plugin.selections[player_uuid]['pos2']
        
        dimension = sender.dimension
        
        min_x, max_x = min(pos1[0], pos2[0]), max(pos1[0], pos2[0])
        min_y, max_y = min(pos1[1], pos2[1]), max(pos1[1], pos2[1])
        min_z, max_z = min(pos1[2], pos2[2]), max(pos1[2], pos2[2])

        width = int(max_x - min_x + 1)
        height = int(max_y - min_y + 1)
        length = int(max_z - min_z + 1)
        
        palette = {}
        palette_id_counter = 0
        
        block_ids = bytearray(width * height * length)
        
        i = 0
        for y in range(min_y, max_y + 1):
            for z in range(min_z, max_z + 1):
                for x in range(min_x, max_x + 1):
                    block = dimension.get_block_at(x, y, z)
                    block_type = str(block.type)
                    
                    if block_type not in palette:
                        palette[block_type] = palette_id_counter
                        palette_id_counter += 1
                    
                    block_ids[i] = palette[block_type]
                    i += 1

        nbt_palette = nbtlib.Compound({name: nbtlib.Int(id) for name, id in palette.items()})

        schematic = nbtlib.File({
            'Schematic': nbtlib.Compound({
                'Width': nbtlib.Short(width),
                'Height': nbtlib.Short(height),
                'Length': nbtlib.Short(length),
                'Materials': nbtlib.String("Alpha"),
                'Blocks': nbtlib.ByteArray(block_ids),
                'Data': nbtlib.ByteArray(bytearray(width * height * length)), # Placeholder
                'Entities': nbtlib.List[nbtlib.Compound]([]),
                'TileEntities': nbtlib.List[nbtlib.Compound]([]),
                'Palette': nbt_palette
            })
        })
        
        schematic_path = plugin.plugin_config.get("schematic-path", "plugins/WorldEdit/schematics")
        file_path = os.path.join(schematic_path, f"{name}.schem")
        schematic.save(file_path, gzipped=True)
        sender.send_message(f"Schematic '{name}.schem' saved.")
        return True

    elif sub_command == "load":
        if len(args) < 2:
            sender.send_message("Usage: /schem load <name>")
            return False
        
        name = args[1]
        schematic_path = plugin.plugin_config.get("schematic-path", "plugins/WorldEdit/schematics")
        file_path = os.path.join(schematic_path, f"{name}.schem")

        if not os.path.exists(file_path):
            sender.send_message(f"Schematic '{name}.schem' not found.")
            return False

        try:
            schematic_file = nbtlib.load(file_path)
            if 'Schematic' not in schematic_file:
                sender.send_message("Invalid schematic: Missing 'Schematic' NBT tag.")
                return False
            schematic = schematic_file['Schematic']
        except Exception as e:
            sender.send_message(f"Error loading schematic file: {e}")
            return False

        width = schematic['Width']
        height = schematic['Height']
        length = schematic['Length']
        
        blocks_to_change = []
        player_uuid = sender.unique_id
        dimension = sender.dimension
        player_location = sender.location

        # Modern schematics use a Palette and BlockData (Sponge Schematic Spec)
        if 'Palette' in schematic and 'BlockData' in schematic:
            palette_nbt = schematic['Palette']
            id_to_name = {v.value: k for k, v in palette_nbt.items()}
            block_data = schematic['BlockData']
            
            sender.send_message(f"Loading modern schematic with Palette ({len(id_to_name)} entries).")
            
            i = 0
            for y in range(height):
                for z in range(length):
                    for x in range(width):
                        # Note: This assumes simple byte array for BlockData.
                        # Real VLE decoding is more complex but this works for many schematics.
                        palette_index = block_data[i]
                        block_name = id_to_name.get(palette_index, "minecraft:air")
                        
                        if block_name != "minecraft:air":
                            target_x = int(player_location.x + x)
                            target_y = int(player_location.y + y)
                            target_z = int(player_location.z + z)
                            blocks_to_change.append((target_x, target_y, target_z, block_name))
                        i += 1

        # Legacy schematics use Blocks and Data arrays (MCEdit/WorldEdit format)
        elif 'Blocks' in schematic:
            sender.send_message("Loading legacy schematic.")
            block_ids = schematic['Blocks']
            block_data = schematic.get('Data', bytearray(len(block_ids)))
            
            i = 0
            for y in range(height):
                for z in range(length):
                    for x in range(width):
                        legacy_id = block_ids[i]
                        # legacy_data = block_data[i] # TODO: Use data for block states
                        
                        block_name = LEGACY_ID_TO_BEDROCK_NAME.get(str(legacy_id), "minecraft:air")
                        
                        if block_name != "minecraft:air":
                            target_x = int(player_location.x + x)
                            target_y = int(player_location.y + y)
                            target_z = int(player_location.z + z)
                            blocks_to_change.append((target_x, target_y, target_z, block_name))
                        i += 1
        else:
            sender.send_message("Invalid or unsupported schematic format: Missing Palette/BlockData or Blocks tags.")
            return False

        sender.send_message(f"Loaded schematic '{name}.schem'. Preparing to place {len(blocks_to_change)} blocks.")

        undo_entry = []
        plugin.redo_history[player_uuid] = []

        # Store blocks for undo before changing them
        for x, y, z, _ in blocks_to_change:
            block = dimension.get_block_at(x, y, z)
            undo_entry.append((x, y, z, str(block.type)))

        if player_uuid not in plugin.undo_history:
            plugin.undo_history[player_uuid] = []
        plugin.undo_history[player_uuid].append(undo_entry)

        affected_blocks = len(blocks_to_change)
        if affected_blocks == 0:
            sender.send_message("Schematic was empty or only contained air.")
            return True

        if affected_blocks > plugin.plugin_config["async-threshold"]:
            plugin.tasks[player_uuid] = {"dimension": dimension, "blocks": blocks_to_change}
            sender.send_message(f"Starting async operation for {affected_blocks} blocks...")
        else:
            for x, y, z, block_type in blocks_to_change:
                block = dimension.get_block_at(x, y, z)
                block.set_type(block_type)
            sender.send_message(f"Operation complete ({affected_blocks} blocks affected).")
        return True

    elif sub_command == "list":
        schematic_path = plugin.plugin_config.get("schematic-path", "plugins/WorldEdit/schematics")
        if not os.path.exists(schematic_path):
            sender.send_message("Schematic directory not found.")
            return False
            
        files = [f for f in os.listdir(schematic_path) if f.endswith('.schem')]
        if not files:
            sender.send_message("No schematics found.")
        else:
            sender.send_message("Available schematics: " + ", ".join([f.replace('.schem', '') for f in files]))
        return True

    sender.send_message(f"Unknown sub-command '{sub_command}'. Use save, load, or list.")
    return False
