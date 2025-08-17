from endstone.plugin import Plugin
from endstone.event import (
    PlayerInteractEvent,
    BlockBreakEvent,
    EventPriority,
    event_handler,
)
import time
import os
import json
from endstone.command import Command, CommandSender, CommandSenderWrapper
from .commands import preloaded_commands, preloaded_handlers


class WorldEditPlugin(Plugin):
    api_version = "0.10"
    commands = preloaded_commands

    def __init__(self):
        super().__init__()
        self.selections = {}
        self.handlers = preloaded_handlers
        self.interaction_cooldown = {}
        self.undo_history = {}
        self.redo_history = {}
        self.clipboard = {}
        self.block_translation_map = {}
        self.particle_toggle = {}  # Stores player UUID -> bool

    def on_load(self):
        self.logger.info("WorldEditPlugin has been loaded!")
        self.load_config()
        
        # Create schematics directory if it doesn't exist
        schematic_path = self.plugin_config.get("schematic-path", "plugins/WorldEdit/schematics")
        if not os.path.exists(schematic_path):
            os.makedirs(schematic_path)

    def load_config(self):
        config_path = "plugins/WorldEdit/config.json"
        default_block_translation_map = {
            "cobblestone_stairs": "stone_stairs",
            "rooted_dirt": "dirt",
            "flowering_azalea_leaves": "azalea_leaves_flowered",
            "slime_block": "slime",
            "sugar_cane": "reeds",
            "small_dripleaf": "small_dripleaf_block",
            "magma_block": "magma",
            "lily_pad": "waterlily",
            "dead_bush": "deadbush",
            "snow_block": "snow",
            "dirt_path": "grass_path",
            "jack_o_lantern": "lit_pumpkin",
            "melon": "melon_block",
            "end_stone_bricks": "end_bricks",
            "end_stone_brick_stairs": "end_brick_stairs",
            "prismarine_brick_stairs": "prismarine_stairs",
            "nether_bricks": "nether_brick",
            "bricks": "brick_block",
            "red_nether_bricks": "red_nether_brick",
            "note_block": "noteblock",
            "cobweb": "web",
            "nether_quartz_ore": "quartz_ore",
            "waxed_copper_block": "copper_block",
            "repeater": "unpowered_repeater",
            "comparator": "unpowered_comparator",
            "powered_rail": "golden_rail",
            "beetroots": "beetroot",
            "oak_door": "wooden_door",
            "oak_trapdoor": "trapdoor",
            "oak_fence": "fence",
            "oak_fence_gate": "fence_gate",
            "oak_button": "wooden_button",
            "oak_pressure_plate": "wooden_pressure_plate",
            "oak_sign": "standing_sign",
            "oak_wall_sign": "wall_sign",
            "warped_sign": "standing_sign",
            "warped_wall_sign": "wall_sign",
            "crimson_sign": "standing_sign",
            "crimson_wall_sign": "wall_sign",
            "bamboo_sign": "standing_sign",
            "bamboo_wall_sign": "wall_sign",
            "cherry_sign": "standing_sign",
            "cherry_wall_sign": "wall_sign",
            "mangrove_sign": "standing_sign",
            "mangrove_wall_sign": "wall_sign",
            "jungle_sign": "standing_sign",
            "jungle_wall_sign": "wall_sign",
            "acacia_sign": "standing_sign",
            "acacia_wall_sign": "wall_sign",
            "dark_oak_sign": "standing_sign",
            "dark_oak_wall_sign": "wall_sign",
            "birch_sign": "standing_sign",
            "birch_wall_sign": "wall_sign",
            "spruce_sign": "standing_sign",
            "spruce_wall_sign": "wall_sign",
            "oak_wall_hanging_sign": "wall_sign",
            "terracotta": "hardened_clay",
            "light_gray_glazed_terracotta": "light_gray_concrete",
            "dark_oak_standing_sign": "standing_sign",
            "sign": "standing_sign",
        }
        default_config = {
            "async-threshold": 5000,
            "particle-type": "minecraft:endrod",
            "particle-density-step": 5,
            "schematic-path": "plugins/WorldEdit/schematics",
            "block_translation_map": default_block_translation_map
        }
        
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            self.plugin_config = default_config
            with open(config_path, 'w') as f:
                json.dump(self.plugin_config, f, indent=4)
        else:
            with open(config_path, 'r') as f:
                self.plugin_config = json.load(f)
        
        self.block_translation_map = self.plugin_config.get("block_translation_map", {})

    def on_enable(self):
        self.logger.info("WorldEditPlugin has been enabled!")
        self.register_events(self)
        self.tasks = {}
        self.silent_sender = CommandSenderWrapper(self.server.command_sender, on_message=lambda msg: None)
        self.server.scheduler.run_task(self, self.run_tasks, delay=1, period=1)
        self.server.scheduler.run_task(self, self.show_selection_particles, delay=20, period=20)  # Every second

    def show_selection_particles(self):
        for player_uuid, selection in self.selections.items():
            # Check if particles are enabled for this player
            if not self.particle_toggle.get(player_uuid, True):
                continue

            if "pos1" in selection and "pos2" in selection:
                player = self.server.get_player(player_uuid)
                if player:
                    pos1 = selection["pos1"]
                    pos2 = selection["pos2"]
                    min_x, max_x = min(pos1[0], pos2[0]), max(pos1[0], pos2[0])
                    min_y, max_y = min(pos1[1], pos2[1]), max(pos1[1], pos2[1])
                    min_z, max_z = min(pos1[2], pos2[2]), max(pos1[2], pos2[2])

                    # Draw a grid of particles along the edges, executed by the player
                    step = self.plugin_config["particle-density-step"]
                    particle_type = self.plugin_config["particle-type"]
                    # Draw a grid of particles along the edges, executed by the player
                    step = self.plugin_config["particle-density-step"]
                    particle_type = self.plugin_config["particle-type"]
                    player_name = player.name
                    
                    def run_particle_command(x, y, z):
                        command = f"execute as {player.name} at @s run particle {particle_type} {x} {y} {z}"
                        self.server.dispatch_command(self.silent_sender, command)

                    for x in range(int(min_x), int(max_x) + 1, step):
                        run_particle_command(x, min_y, min_z)
                        run_particle_command(x, max_y, min_z)
                        run_particle_command(x, min_y, max_z)
                        run_particle_command(x, max_y, max_z)
                    for y in range(int(min_y), int(max_y) + 1, step):
                        run_particle_command(min_x, y, min_z)
                        run_particle_command(max_x, y, min_z)
                        run_particle_command(min_x, y, max_z)
                        run_particle_command(max_x, y, max_z)
                    for z in range(int(min_z), int(max_z) + 1, step):
                        run_particle_command(min_x, min_y, z)
                        run_particle_command(max_x, min_y, z)
                        run_particle_command(min_x, max_y, z)
                        run_particle_command(max_x, max_y, z)

    def run_tasks(self):
        for player_uuid, task_info in list(self.tasks.items()):
            dimension = task_info["dimension"]
            blocks_to_change = task_info["blocks"]
            
            # Process a chunk of blocks each tick
            chunk_size = self.plugin_config["async-threshold"]
            for _ in range(chunk_size):
                if not blocks_to_change:
                    player = self.server.get_player(player_uuid)
                    if player:
                        player.send_message("Async operation complete.")
                    del self.tasks[player_uuid]
                    break
                
                # Unpack data, now including the data value
                try:
                    if not blocks_to_change:
                        break
                    block_data = blocks_to_change.pop(0)
                    
                    # Handle both 4-value and 5-value tuples for compatibility
                    if len(block_data) == 5:
                        x, y, z, block_type, data_value = block_data
                    else:
                        x, y, z, block_type = block_data
                        data_value = None

                    block = dimension.get_block_at(x, y, z)
                    block.set_type(block_type)
                    if data_value is not None:
                        block.set_data(data_value) # Assuming data_value is the saved block data
                except RuntimeError as e:
                    self.logger.error(f"Skipping block '{block_type}' for player {player_uuid}: {e}")
                    player = self.server.get_player(player_uuid)
                    if player:
                        player.send_message(f"§cSkipped block: {block_type} ({e})§r")
                    continue  # Skip to the next block

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name in self.handlers:
            handler = self.handlers[command.name]
            return handler(self, sender, args)
        return False

    @event_handler(priority=EventPriority.HIGH)
    def on_block_break(self, event: BlockBreakEvent):
        player = event.player
        item = player.inventory.item_in_main_hand
        if item is not None and item.type == "minecraft:wooden_axe":
            event.cancel()
            player_uuid = player.unique_id
            if player_uuid not in self.selections:
                self.selections[player_uuid] = {}
            block = event.block
            self.selections[player_uuid]["pos1"] = (block.x, block.y, block.z)
            player.send_message(f"Position 1 set to ({block.x}, {block.y}, {block.z}).")

    @event_handler(priority=EventPriority.HIGH)
    def on_player_interact(self, event: PlayerInteractEvent):
        player = event.player
        player_uuid = player.unique_id
        current_time = time.time()

        last_interact_time = self.interaction_cooldown.get(player_uuid, 0)
        if current_time - last_interact_time < 0.1:  # 100ms cooldown
            return

        if event.action.name == "RIGHT_CLICK_BLOCK":
            item = player.inventory.item_in_main_hand
            if item is not None and item.type == "minecraft:wooden_axe":
                self.interaction_cooldown[player_uuid] = current_time
                if player_uuid not in self.selections:
                    self.selections[player_uuid] = {}
                block = event.block
                self.selections[player_uuid]["pos2"] = (block.x, block.y, block.z)
                player.send_message(f"Position 2 set to ({block.x}, {block.y}, {block.z}).")
