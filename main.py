import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Placeholder, Input, Static, Label, TextArea
from pathlib import Path
from textual.events import Click
from textual.coordinate import Coordinate
from textual.geometry import Offset
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer, Grid

from lib import DataManager
from lib import ToggleTree
from lib import InfoDisplay

class Namnbyte(App[None]):
    BINDINGS = [
        Binding("1", "focus_tree", "Focus on Tree View", show=True),
        Binding("2", "focus_data_table", "Focus on Data Table", show=True),
        Binding("3", "focus_input", "Focus on Input Field", show=True),
    ]

    CSS_PATH = "assets/main.tcss"

    def __init__(self, path: Path):
        super().__init__()
        self.current_directory = path
        self.data_manager = DataManager(path)
        self.data_manager.add_observer(self)

        self.column_mapping = [
            {"name": " ", "key": "is_enabled"},
            {"name": "Extension", "key": "file_ext"},
            {"name": "Current Name", "key": "current_name"},
            {"name": "New Name", "key": "new_name"},
            {"name": "Size", "key": "size"},
            {"name": "Path", "key": "rel_path"},
        ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with Grid():
            with ScrollableContainer(id="left_panel"):
                self.toggle_tree = ToggleTree(label="✅📂 Current Directory", id="tree_display", data_manager=self.data_manager, directory_path=self.current_directory)
                yield self.toggle_tree
                self.info_display = InfoDisplay(data_manager=self.data_manager, id="info_display", expand=True)
                yield self.info_display
            with Vertical(id="right_panel"):
                self.data_table =  DataTable(id="file_table")
                yield self.data_table
                with Vertical(id="right_sub_panel"):
                    yield Label(id="output_display", expand=True)
                    self.input_field = Input(id="input_command")
                    yield self.input_field

    def on_mount(self) -> None:
        tree = self.toggle_tree
        self.data_table.border_title = "Files"
        self.tree.guide_depth = 2
        self.data_manager.populate_tree(tree.root, self.current_directory, recursive=False)
        tree.focus()
        self.initialize_file_table()
        self.populate_file_table()

    def initialize_file_table(self):
        file_table = self.data_table
        file_table.clear()

        # Add columns based on the column_mapping
        for column in self.column_mapping:
            file_table.add_column(column["name"])

    def populate_file_table(self):
        file_table = self.data_table
        file_table.clear()

        for folder_data in self.data_manager.data["folders"].values():
            if not folder_data["is_enabled"]:
                    continue
            for file_data in folder_data["files"]:
                if not file_data["is_enabled"]:
                    continue
                self._add_file_row(file_data)

    def _add_file_row(self, file_data):
        file_table = self.data_table

        # Dynamically create the row using the keys from column_mapping
        row = [self._get_file_data(file_data, column["key"]) for column in self.column_mapping]

        # Add the row in the same order as the columns
        file_table.add_row(*row)

    def _get_file_data(self, file_data, key):
        """Helper function to return the appropriate value for each column."""
        if key == "is_enabled":
            return "✅" if file_data[key] else "❌"
        return file_data[key]

    def update_file_table(self):
        # self.update_info_display()
        file_table = self.data_table
        file_table.clear()

        for folder_data in self.data_manager.data["folders"].values():
            if folder_data["is_enabled"]:
                for file_data in folder_data["files"]:
                    self._add_file_row(file_data)

    def get_enabled_folders(self, node):
        """Get enabled folders from FolderDataManager."""
        return self.data_manager.get_enabled_folders(node)
    
    def update(self, updated_data):
        """Handle updates from the DataManager."""
        if "folder" in updated_data:
            folder_data = updated_data["folder"]
            self.update_file_table()  # Refresh the table to reflect the folder data changes
        if "file" in updated_data:
            file_data = updated_data["file"]
            self.update_file_table()  # Refresh the table to reflect the file data changes
        if "summary" in updated_data:
            self.info_display.refresh_display()
            # self.update_info_display()  # Refresh the info display if the summary changes
        if "batch_update_done" in updated_data:
            self.update_file_table()  # Refresh the file table after a batch update

    def action_focus_tree(self) -> None:
        """Focus on the tree view panel."""
        self.toggle_tree.focus()

    def action_focus_data_table(self) -> None:
        """Focus on the data table panel."""
        self.data_table.focus()

    def action_focus_input(self) -> None:
        """Focus on the input field panel."""
        self.input_field.focus()

    # Call this method to start a batch update
    def start_batch_update(self):
        self.data_manager.start_batch_update()

    # Call this method to end the batch update
    def end_batch_update(self):
        self.data_manager.end_batch_update()

if __name__ == "__main__":
    Namnbyte(path=Path(".")).run()