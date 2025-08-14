from endstone.plugin import Plugin
from endstone.event import (
    PlayerInteractEvent,
    BlockBreakEvent,
    EventPriority,
    event_handler,
)
import time
from endstone.command import Command, CommandSender
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

    def on_enable(self):
        self.logger.info("WorldEditPlugin has been enabled!")
        self.register_events(self)

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
