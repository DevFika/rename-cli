import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, DataTable
from pathlib import Path
from textual.events import Click
from textual.coordinate import Coordinate
from textual.geometry import Offset
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer

from lib import DataManager

# ✅
ENABLED_FOLDER = f"[green]■[/green]"
DISABLED_FOLDER = f"[red]■[/red]"
class ToggleTree(Tree[bool]):
    BINDINGS = [
    Binding("a", "toggle_expand_all", "Expand all", show=True,),
    Binding("q", "toggle_collapse_all", "Collapse all", show=True,),
    Binding("x", "disable_all", "Disable all", show=True,),
    ]

    def on_mount(self):
        self.root.is_enabled = True
        self.root.path = Path(".")
        self.styles.border = ("round", "yellow")
        self.border_title = "Folder Tree"
        self.styles.background = "black"
        return super().on_mount()
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.prevent_default()

        if event.node == self.root:
            self.root.is_enabled = not self.root.is_enabled
            self.update_node_label(self.root)
            self.app.update_folder_data(self.root)  # Update data structure
        else:
            event.node.is_enabled = not event.node.is_enabled
            self.update_node_label(event.node)
            self.app.update_folder_data(event.node)  # Update data structure

        # Recalculate the summary and update the file table
        self.app.recalculate_summary()  # Update the summary
        self.app.update_file_table()    # Update the file table


    def update_node_label(self, node):
        if node == self.root:
            node.label = f"{ENABLED_FOLDER} {node.label.plain.split(' ', 1)[1]}" if node.is_enabled else f"{DISABLED_FOLDER} {node.label.plain.split(' ', 1)[1]}"
            node.styles = "bold green" if node.is_enabled else "bold red"
        if node.is_enabled:
            node.label = f"{ENABLED_FOLDER} {node.label.plain.split(' ', 1)[1]}" # Green Square
            node.styles = "bold green"
        else:
            node.label = f"{DISABLED_FOLDER} {node.label.plain.split(' ', 1)[1]}" # Red Square
            node.styles = "bold red"


    def action_toggle_expand_all(self):
        self.root.expand_all()

    def _disable_node(self, node):
        node.is_enabled = False
        self.update_node_label(node)

        self.app.update_folder_data(node)

        for child in node.children:
            self._disable_node(child)

    def action_disable_all(self):
        self._disable_node(self.root)
        self.app.update_file_table()

    def action_toggle_collapse_all(self):
        self.root.collapse_all()

class FileRenamerApp(App[None]):
    BINDINGS = [
        Binding("k", "space", "Expand or collapse all", show=True),
    ]
    def __init__(self, path: Path):
        super().__init__()
        self.current_directory = path
        self.data_manager = DataManager(path)

        self.data = {
            "folders": {},
            "summary": {
                "folders_count": 0,
                "enabled_folders_count": 0,
                "files_count": 0,
                "enabled_files_count": 0,
                "total_size": 0,
            }
        }

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        yield Horizontal(
            Container(
                ScrollableContainer(
                    ToggleTree("📂 Current Directory", id="tree"),
                    id="folder_container"
                ),
                id="left_panel"
            ),
            Container(
                ScrollableContainer(
                    Vertical(
                        DataTable(id="file_table"),
                    ),
                    id="file_container"
                ),
                id="right_panel"
            ),
            id="main_container"
        )
        # yield ToggleTree("📂 Current Directory", id="tree")

    def on_mount(self) -> None:
        tree = self.query_one(ToggleTree)
        # tree.show_root = False
        tree.guide_depth = 2
        self.data_manager.populate_tree(tree.root, self.current_directory)
        # self.populate_tree(tree.root, self.current_directory)
        tree.focus()
        self.query_one("#left_panel").styles.width = "25%"
        self.initialize_file_table()
        self.update_file_table() 
        # print(tree.get_bindings())  # Print registered bindings for debugging
    
    def initialize_file_table(self):
        # Initialize DataTable with columns once
        file_table = self.query_one(DataTable)
        file_table.add_column("File Name")
        file_table.add_column("Size")


    def update_file_table(self):
        # Get all enabled folders from the tree
        # tree = self.query_one(ToggleTree)
        # enabled_folders = self.get_enabled_folders(tree.root)

        # Now filter and display files from enabled folders in the data table
        file_table = self.query_one(DataTable)
        file_table.clear()

        # Now display files based on the central data structure
        for folder_data in self.data_manager.data["folders"].values():
            if folder_data["is_enabled"]:
                for file_data in folder_data["files"]:
                    if file_data["is_enabled"]:
                        file_table.add_row(file_data["name"], str(file_data["size"]))

    def update_folder_data(self, node):
        """Delegate folder data update to the FolderDataManager."""
        self.data_manager.update_folder_data(node)
        self.data_manager.recalculate_summary()
        self.update_file_table()

    def recalculate_summary(self):
        """Recalculate the summary of enabled folders and files."""
        self.data_manager.recalculate_summary()

    def get_enabled_folders(self, node):
        """Get enabled folders from FolderDataManager."""
        return self.data_manager.get_enabled_folders(node)
    
if __name__ == "__main__":
    FileRenamerApp(path=Path(".")).run()