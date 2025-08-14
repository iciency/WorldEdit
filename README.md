# WorldEdit for Endstone

A powerful WorldEdit-like plugin for the Endstone Minecraft server software, offering a suite of commands to modify the world.

## Features

-   **Selections**: Define a region using a wand or position commands.
-   **Editing**: Fill selections with blocks (`/set`), or clear them (`/cut`).
-   **Shape Generation**: Create solid/hollow spheres (`/sphere`, `/hsphere`) and cylinders (`/cyl`, `/hcyl`).
-   **Clipboard**: Copy (`/copy`) and paste (`/paste`) selections.
-   **History**: Undo (`/undo`) and redo (`/redo`) your actions.
-   **Schematics**: Save and load selections in the `.schem` (Java Edition compatible) format.
-   **Permissions**: Fine-grained permission nodes for each command (e.g., `worldedit.command.set`).

## Installation

1.  **Build the Project:**
    If you don't have the `build` package, install it first:
    ```bash
    pip install build
    ```
    Then, build the plugin from the project's root directory (where `pyproject.toml` is located):
    ```bash
    python -m build
    ```
    This will create a `.whl` file in the `dist` folder. This is your Endstone plugin.

2.  **Install the Plugin:**
    Copy or move the generated `.whl` file (e.g., `dist/endstone_worldedit-1.0.0-py3-none-any.whl`) into your Endstone server's `plugins` folder.

3.  **Restart the Server:**
    Start or restart your Endstone server to load the plugin.

## Usage

**Note:** All commands require specific permissions. By default, only server operators (OP) have these permissions. Use a permission management plugin to grant them to other players.

1.  **Get the Selection Wand:**
    In the game, type the following command to get the wooden axe (the selection tool):
    ```
    /wand
    ```

2.  **Select a Region:**
    -   **Set Position 1 (Pos1):** With the wand in hand, **left-click** a block. A message "Position 1 set to (x, y, z)." will appear.
    -   **Set Position 2 (Pos2):** With the wand in hand, **right-click** another block. A message "Position 2 set to (x, y, z)." will appear.
    -   **Alternatively**, you can use the `/pos1` and `/pos2` commands to set the positions to your current location.

3.  **Modify the Selection:**
    Once both positions are set, you can use the following commands:

    -   **Set Blocks:**
        Fill the selected region with a specific block.
        ```
        /set <block_name>
        ```
        Example: `/set minecraft:stone`

    -   **Replace Blocks:**
        Replace all blocks of a certain type with another within the selection.
        ```
        /replace <from_block> <to_block>
        ```
        Example: `/replace minecraft:dirt minecraft:glass`

    -   **Create Walls:**
        Create walls around the outer edges of the selection.
        ```
        /walls <block>
        ```

    -   **Overlay Blocks:**
        Place a layer of blocks on top of the selection.
        ```
        /overlay <block>
        ```

    -   **Cut Blocks:**
        Remove all blocks in the selection (replaces them with air).
        ```
        /cut
        ```

4.  **Generate Shapes:**
    Create shapes at your current location.

    -   **Spheres:**
        Create a solid or hollow sphere.
        ```
        /sphere <block> <radius>
        /hsphere <block> <radius>
        ```

    -   **Cylinders:**
        Create a solid or hollow cylinder. Height is optional and defaults to 1.
        ```
        /cyl <block> <radius> [height]
        /hcyl <block> <radius> [height]
        ```

5.  **Use the Clipboard:**

    -   **Copy:**
        Copy the blocks within the selection to your clipboard. The copy is relative to your position.
        ```
        /copy
        ```

    -   **Paste:**
        Paste the copied blocks at your current location.
        ```
        /paste
        ```

6.  **Manage Schematics:**
    Save and load structures to files.

    -   **Save:**
        Save the current selection to a `.schem` file.
        ```
        /schem save <name>
        ```

    -   **Load:**
        Load a `.schem` file at your current position.
        ```
        /schem load <name>
        ```

    -   **List:**
        List all available schematics.
        ```
        /schem list
        ```

7.  **Manage History:**

    -   **Undo:**
        Revert your last action (`/set`, `/replace`, `/walls`, `/overlay`, `/cut`, `/paste`, shape generation, or `/schem load`).
        ```
        /undo
        ```

    -   **Redo:**
        Restore an action that you just undid.
        ```
        /redo
