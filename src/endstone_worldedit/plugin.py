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

    def on_load(self):
        self.logger.info("WorldEditPlugin has been loaded!")
        self.load_config()
        
        # Create schematics directory if it doesn't exist
        schematic_path = self.plugin_config.get("schematic-path", "plugins/WorldEdit/schematics")
        if not os.path.exists(schematic_path):
            os.makedirs(schematic_path)

    def load_config(self):
        config_path = "plugins/WorldEdit/config.json"
        default_config = {
            "async-threshold": 5000,
            "particle-type": "minecraft:endrod",
            "particle-density-step": 5,
            "schematic-path": "plugins/WorldEdit/schematics"
        }
        
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            self.plugin_config = default_config
            with open(config_path, 'w') as f:
                json.dump(self.plugin_config, f, indent=4)
        else:
            with open(config_path, 'r') as f:
                self.plugin_config = json.load(f)
            # Ensure all keys are present
            for key, value in default_config.items():
                if key not in self.plugin_config:
                    self.plugin_config[key] = value
            with open(config_path, 'w') as f:
                json.dump(self.plugin_config, f, indent=4)

    def on_enable(self):
        self.logger.info("WorldEditPlugin has been enabled!")
        self.register_events(self)
        self.tasks = {}
        self.silent_sender = CommandSenderWrapper(self.server.command_sender, on_message=lambda msg: None)
        self.server.scheduler.run_task(self, self.run_tasks, delay=1, period=1)
        self.server.scheduler.run_task(self, self.show_selection_particles, delay=20, period=20)  # Every second

    def show_selection_particles(self):
        for player_uuid, selection in self.selections.items():
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
                    x, y, z, block_type, data_value = block_data
                    block = dimension.get_block_at(x, y, z)
                    block.set_type(block_type)
                    if data_value is not None:
                        block.data = data_value
                except RuntimeError as e:
                    player = self.server.get_player(player_uuid)
                    if player:
                        player.send_message(f"§cSkipped block: {block_type} ({e})§r")
                    continue # Skip to the next block

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
            event.cancelled = True
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
