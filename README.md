# WorldEdit for Endstone

A powerful WorldEdit-like plugin for the Endstone Minecraft server software, offering a suite of commands to modify the world.

## Features

-   **Selections**: Define a region using a wand or position commands.
-   **Editing**: Fill selections with blocks (`/set`), or clear them (`/cut`).
-   **Clipboard**: Copy (`/copy`) and paste (`/paste`) selections.
-   **History**: Undo (`/undo`) and redo (`/redo`) your actions.
-   **Permissions**: All commands are restricted to server operators (OP) only.

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

**Note:** All commands require operator (OP) permissions.

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

    -   **Cut Blocks:**
        Remove all blocks in the selection (replaces them with air).
        ```
        /cut
        ```

4.  **Use the Clipboard:**

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

5.  **Manage History:**

    -   **Undo:**
        Revert your last action (`/set`, `/cut`, or `/paste`).
        ```
        /undo
        ```

    -   **Redo:**
        Restore an action that you just undid.
        ```
        /redo
