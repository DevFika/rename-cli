import os
from textual import on
from textual.screen import ModalScreen
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Placeholder, Input, Static, Label, TextArea
from pathlib import Path
from textual.events import Click, Focus, InputEvent
from textual.coordinate import Coordinate
from textual.geometry import Offset
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer, Grid
from typing import Callable
from textual.suggester import SuggestFromList
from rich.text import Text

from lib import DataManager, ToggleTree, InfoDisplay, FileTable, EditCellRequested
from lib import FileTableColumns, EditCellScreen, process_names, CommandSuggester, CommandHandler

class Namnbyte(App[None]):
    BINDINGS = [
        Binding("1", "focus_tree", "Focus on Tree View", show=True),
        Binding("f1", "focus_tree", "Focus on Tree View", show=False),
        Binding("2", "focus_data_table", "Focus on Data Table", show=True),
        Binding("f2", "focus_data_table", "Focus on Data Table", show=False),
        Binding("3", "focus_input", "Focus on Input Field", show=True),
        Binding("f3", "focus_input", "Focus on Input Field", show=False),
        Binding("u", "test", "Focus on Input Field", show=True),
    ]

    CSS_PATH = "assets/main.tcss"

    def __init__(self, path: Path):
        super().__init__()
        self.current_directory = path
        self.data_manager = DataManager(path)
        self.data_manager.add_observer(self)

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
                self.data_table = FileTable(data_manager=self.data_manager, id="file_table")
                yield self.data_table
                with Vertical(id="right_sub_panel"):
                    yield Label(id="output_display", expand=True)
                    self.input_field = Input(id="input_command")
                    self.input_field.suggester = CommandSuggester()
                    yield self.input_field

    def on_mount(self) -> None:
        tree = self.toggle_tree
        self.data_table.border_title = "Files"
        self.tree.guide_depth = 2
        self.data_manager.populate_tree(tree.root, self.current_directory, recursive=False)
        self.data_table.populate_table()
        tree.focus()

    def update(self, updated_data):
        """Handle updates from the DataManager."""
        if "folder" in updated_data:
            folder_data = updated_data["folder"]
            self.data_table.populate_table()  # Refresh the table to reflect the folder data changes
        if "file" in updated_data:
            file_data = updated_data["file"]
            self.data_table.update_file_row(file_data)
        if "summary" in updated_data:
            self.info_display.refresh_display()
        if "batch_update_done" in updated_data:
            self.data_table.populate_table()  # Refresh the file table after a batch update
        if "name_processing_done" in updated_data:
            self.data_table.populate_table()  # Refresh the file table after a batch update

    def action_test(self) -> None:
        print("Starting action test...")
        self.data_manager.set_file_name("test", "2", "pop")

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

    @on(EditCellRequested)
    def handle_edit_cell_requested(self, event: EditCellRequested):
        def on_complete(new_value: str):
            folder_path_column_index = FileTableColumns.get_column_index(FileTableColumns.FOLDER_PATH.value["key"])
            current_name_column_index = FileTableColumns.get_column_index(FileTableColumns.CURRENT_NAME.value["key"])

            folder_path = event.sender.get_cell_at((event.row, folder_path_column_index))  # Get the folder path
            old_name = event.sender.get_cell_at((event.row, current_name_column_index))  # Get the old name

            if isinstance(folder_path, Text):
                folder_path = folder_path.plain

            if isinstance(old_name, Text):
                old_name = old_name.plain

            value = new_value
            if isinstance(value, Text):
                value = value.plain

            self.data_manager.set_file_name(folder_path, old_name, value)

        self.push_screen(EditCellScreen(event.value, on_complete))

    @on(Input.Submitted, "#input_command")
    def handle_input_command(self, event: Input.Submitted):
        input_command = event.value
        command_handler = CommandHandler(input_command)
        command_handler.handle_input()
        # process_names(input_command, self.data_manager)
        self.input_field.clear()


if __name__ == "__main__":
    Namnbyte(path=Path("./test")).run()