# WorldEdit for Endstone

A powerful and intuitive WorldEdit-like plugin for the Endstone Minecraft server software, offering a comprehensive suite of commands to modify the world efficiently.

## Features

-   **Intuitive Selections**: Define a 3D region using a classic wand (`/wand`) or precise position commands (`/pos1`, `/pos2`).
-   **Versatile Block Editing**: Set blocks in a region (`/set`), replace specific blocks (`/replace`), build walls (`/walls`), or drape a layer of blocks over the terrain (`/overlay`).
-   **Advanced Clipboard**: Copy (`/copy`), cut (`/cut`), and paste (`/paste`) complex structures relative to your position.
-   **Reliable History**: Easily undo (`/undo`) and redo (`/redo`) your actions to correct mistakes without hassle.
-   **Procedural Generation**: Create perfect solid (`/sphere`, `/cyl`) and hollow (`/hsphere`, `/hcyl`) shapes like spheres and cylinders.
-   **Cross-Edition Schematics**: Save and load structures to and from `.schem` files. The plugin is designed to handle compatibility between Java Edition and Bedrock Edition formats.
-   **Flexible Configuration**: Customize plugin behavior and, most importantly, add custom block name translations via `config.json` to resolve schematic compatibility issues on the fly.
-   **Granular Permissions**: Fine-grained permission nodes for every command (e.g., `worldedit.command.set`) for precise server management.

## Installation

1.  **Build the Project:**
    First, ensure you have the Python `build` package:
    ```bash
    pip install build
    ```
    Then, build the plugin from the project's root directory:
    ```bash
    python -m build
    ```
    This will create a `.whl` file in the `dist/` folder.

2.  **Install the Plugin:**
    Copy the generated `.whl` file (e.g., `dist/endstone_worldedit-1.0.0-py3-none-any.whl`) into your Endstone server's `plugins/` folder.

3.  **Restart the Server:**
    Start or restart your Endstone server to load the plugin and generate the default configuration.

## Configuration

Upon first launch, the plugin will create a `config.json` file in `plugins/WorldEdit/`. This file allows you to customize the plugin's behavior.

**Note:** When updating the plugin to a new version, it is recommended to delete your existing `config.json` file. This allows the plugin to generate a new one with the latest default settings and translation rules.

```json
{
    "async-threshold": 5000,
    "particle-type": "minecraft:endrod",
    "particle-density-step": 5,
    "schematic-path": "plugins/WorldEdit/schematics",
    "block_translation_map": {
        "cobblestone_stairs": "stone_stairs",
        "rooted_dirt": "dirt",
        "sugar_cane": "reeds",
        "slime_block": "slime",
        "oak_sign": "standing_sign",
        "oak_wall_sign": "wall_sign"
    }
}
```

-   **`async-threshold`**: The number of blocks at which an operation will be processed in smaller chunks to prevent server lag.
-   **`particle-type`**: The particle used to visualize the selection box.
-   **`block_translation_map`**: A powerful feature for resolving compatibility issues when loading Java Edition schematics. If a schematic fails to load because a block name isn't found (e.g., Java's `minecraft:slime_block`), you can add an entry here to translate it to the correct Bedrock name (e.g., `"slime_block": "slime"`).

## Usage Guide

**Note:** All commands require specific permissions (e.g., `worldedit.command.wand`). By default, only server operators have these permissions.

### 1. The Selection Wand
First, give yourself the selection tool.
-   **/wand** (Alias: `/w`): Gives you a wooden axe to use as the selection wand.

### 2. Selecting a Region
Define the area you want to edit.
-   **Left-Click** a block with the wand to set **Position 1**.
-   **Right-Click** a block with the wand to set **Position 2**.
-   **/pos1** & **/pos2**: Sets your current location as Position 1 or 2.

### 3. Editing the World
Modify the blocks within your selection.
-   **/set `<block>`**: Fills the entire selection with a block.
-   **/replace `<from_block>` `<to_block>`**: Replaces all instances of one block with another.
-   **/cut**: Deletes all blocks in the selection and copies them.
-   **/walls `<block>`**: Builds walls on the outer edges of the selection.
-   **/overlay `<block>`**: Places a layer of blocks on top of the highest blocks in the selection.

### 4. Clipboard and History
Manage your copied selections and actions.
-   **/copy**: Copies the selected region.
-   **/paste**: Pastes the copied selection at your location.
-   **/undo**: Reverts your last action.
-   **/redo**: Restores the action you just undid.

### 5. Generating Shapes
Create perfect geometric shapes.
-   **/sphere `<block>` `<radius>`**: Creates a solid sphere.
-   **/hsphere `<block>` `<radius>`**: Creates a hollow sphere.
-   **/cyl `<block>` `<radius>` `[height]`**: Creates a solid cylinder.
-   **/hcyl `<block>` `<radius>` `[height]`**: Creates a hollow cylinder.

### 6. Schematics
Save and load your creations.
-   **/schem save `<name>`**: Saves the selection to `<name>.schem`.
-   **/schem load `<name>`**: Loads a schematic file at your location.
-   **/schem list**: Lists all available schematics.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository. If you would like to contribute code, please fork the repository and submit a pull request.
