import importlib
import pkgutil
import os

preloaded_commands = {}
preloaded_handlers = {}

def preload_commands():
    """Preload all command modules."""
    global preloaded_commands, preloaded_handlers
    
    print("[WorldEdit] Registering commands...")
    commands_base_path = os.path.dirname(__file__)
    
    for _, module_name, _ in pkgutil.iter_modules([commands_base_path]):
        if module_name == "__init__":
            continue
        module_import_path = f"endstone_worldedit.commands.{module_name}"
        module = importlib.import_module(module_import_path)

        if hasattr(module, 'command') and hasattr(module, 'handler'):
            for cmd, details in module.command.items():
                print(f"✓ {cmd} - {details.get('description', 'No description')}")
                preloaded_commands[cmd] = details
                preloaded_handlers[cmd] = module.handler
    print("\n")

# Run preload automatically when this file is imported
preload_commands()
