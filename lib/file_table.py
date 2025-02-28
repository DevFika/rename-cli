from textual.widgets import DataTable, Input, RichLog, Select
from textual.screen import ModalScreen, Screen
from textual.events import Click
from textual.app import ComposeResult
from textual import on
from lib import DataManager
from typing import Any
from rich.text import Text
import difflib

from .columns import FileTableColumns

def highlight_changes(original, new):
    """Highlight differences between original and new name using rich.Text."""
    matcher = difflib.SequenceMatcher(None, original, new)
    
    highlighted_original = Text()
    highlighted_new = Text()

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            highlighted_original.append(original[i1:i2], style="dim")
            highlighted_new.append(new[j1:j2])
        elif tag == "replace" or tag == "insert":
            highlighted_new.append(new[j1:j2], style="bold green")
            highlighted_original.append(original[i1:i2], style="bold red")
        elif tag == "delete":
            highlighted_original.append(original[i1:i2], style="bold red")

    return highlighted_original, highlighted_new

class FileTable(DataTable):
    CSS_PATH = "../assets/file_table.tcss"
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.row_metadata = {}
        self.column_sort_order = {}
        self.column_mapping = FileTableColumns.get_all_columns()
        self.initialize_table()

    def get_column_index_by_key(self, column_key):
        """Helper function to get column index by key using the Enum."""
        return FileTableColumns.get_column_index(self.column_mapping, column_key)

    def get_column_name_by_key(self, column_key):
        """Helper function to get column name by key using the Enum."""
        return FileTableColumns.get_column_name(column_key)

    @on(DataTable.CellSelected)
    def data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        # Extracting the cell value
        cell_value = event.value
        selected_column_index = event.coordinate.column
        message = (
            f"Original value of cell at {event.coordinate}"
            f" is {event.value} and type {type(event.value)}"
        )

        rel_path_column_index = self.get_column_index_by_key(FileTableColumns.REL_PATH.value["key"])
        is_enabled_index = self.get_column_index_by_key(FileTableColumns.IS_ENABLED.value["key"])
        current_name_index = self.get_column_index_by_key(FileTableColumns.CURRENT_NAME.value["key"])
        new_name_index = self.get_column_index_by_key(FileTableColumns.NEW_NAME.value["key"])
        folder_path_column_index = self.get_column_index_by_key(FileTableColumns.FOLDER_PATH.value["key"])

        current_row = event.coordinate.row

        # Ensure the indices were found before proceeding
        if None in [rel_path_column_index, is_enabled_index, current_name_index]:
            print("Error: One or more column indices were not found.")
            return

        # Access the values for rel_path, is_enabled, and current_name for the current row
        rel_path_value = self.get_cell_at((current_row, rel_path_column_index))
        is_enabled_value = self.get_cell_at((current_row, is_enabled_index))
        current_name_value = self.get_cell_at((current_row, current_name_index))
        folder_value = self.get_cell_at((current_row, folder_path_column_index))
        if isinstance(folder_value, Text):
            folder_value = folder_value.plain
        if isinstance(current_name_value, Text):
            current_name_value = current_name_value.plain
        if isinstance(rel_path_value, Text):
            rel_path_value = rel_path_value.plain
        if isinstance(is_enabled_value, Text):
            is_enabled_value = is_enabled_value.plain
        if isinstance(cell_value, Text):
            cell_value = cell_value.plain
        # Print the message and the retrieved values
        print(message)
        print(f"Rel Path: {rel_path_value}")
        print(f"Is Enabled: {is_enabled_value}")
        print(f"Current Name: {current_name_value}")

        if selected_column_index == is_enabled_index:
            print("Lets toggle file")

            self.data_manager.toggle_file_enabled(folder_value, current_name_value)
        elif selected_column_index == new_name_index:
            print("Lets push edit cell")
            self.post_message(EditCellRequested(self, current_row, selected_column_index, cell_value))


        # if rel_path_column_index is not None:
        #     # Access the row data using the correct column index dynamically
        #     current_row = event.coordinate.row
        #     rel_path = self.get_cell_at((current_row, rel_path_column_index))

        #     # For demonstration, print the message and the rel_path
        #     print(message)
        #     print(f"Rel Path: {rel_path}")
        # current_row = event.coordinate.row
        # rel_path = self.get_cell_at((current_row, 6))

        # if event.coordinate.column == 3:
        #     print(message)
        # row_data = self.data_manager.get(event.coordinate.row, {})
        # rel_path = row_data.get("5", None)
        # print(rel_path)
        # # rel_path = this column index 5, how do I fetch that?

        # rel_path = row_data.get('rel_path', None)  # You can access the row based on rel_path key

        # You can now use this to find the row data
        # Assuming self.data_manager holds your data in a dict or similar structure keyed by 'rel_path':
        # row_data = self.data_manager.get(rel_path, {})  # Get the row data based on the relative path key

        # # Dynamically get the key for the "Folder Path" column
        # folder_path_key = next(
        #     (col["key"] for col in self.column_mapping if col["name"] == "Folder Path"),
        #     None
        # )
        # print(folder_path_key)
        # folder_path = row_data.get(folder_path_key, None) if folder_path_key else None

        # print(message)
        # print(f"Folder Path: {folder_path}")

    def initialize_table(self):
        self.clear()
        for index, column in enumerate(self.column_mapping):
            self.add_column(column["name"], key=str(index))

    def populate_table(self):
        self.clear()
        for folder_data in self.data_manager.data["folders"].values():
            if not folder_data["is_enabled"]:
                continue
            for file_data in folder_data["files"]:
                # if not file_data["is_enabled"]:
                #     continue
                print(file_data)
                self.add_file_row(file_data)

    def add_file_row(self, file_data):
        # Create a list to store the row, applying highlight changes to current_name and new_name
        row = []
        
        for column in self.column_mapping:
            # Get the value for the current column
            value = self.get_file_data(file_data, column["key"])
            
            # If the column is either current_name or new_name, apply highlighting
            if column["key"] == "current_name":
                original_name = value
                new_name = file_data.get("new_name", "")
                highlighted_current, _ = highlight_changes(original_name, new_name)
                row.append(highlighted_current)  # Add the highlighted current name
            elif column["key"] == "new_name":
                original_name = file_data.get("current_name", "")
                new_name = value
                _, highlighted_new = highlight_changes(original_name, new_name)
                row.append(highlighted_new)  # Add the highlighted new name
            else:
                # For other columns, add the value as plain text
                row.append(Text(str(value)))

        # Apply additional classes for styling if necessary
        classes = []
        if not file_data.get("is_enabled"):
            classes.append("disabled")
        if file_data.get("current_name") != file_data.get("new_name"):
            classes.append("pending-change")

        # Add the row to the table with the appropriate classes
        self.add_row(*row, key=file_data["rel_path"])

    # def old_add_file_row(self, file_data):
    #     row = [
    #         Text(str(self.get_file_data(file_data, column["key"])), style="italic #03AC13", justify="right")
    #         for column in self.column_mapping
    #     ]
    #     # row = [self.get_file_data(file_data, column["key"]) for column in self.column_mapping]
    #     classes = []
    #     if not file_data.get("is_enabled"):
    #         classes.append("disabled")
    #     if file_data.get("current_name") != file_data.get("new_name"):
    #         classes.append("pending-change")
    #     self.add_row(*row, key=file_data["rel_path"])

    def update_file_row(self, file_data):
        """Update a file row with highlighted changes for current_name and new_name."""
        rel_path = file_data["rel_path"]
        if rel_path not in self.rows:
            return

        # Iterate over each column to update the relevant cells
        for column_index, column in enumerate(self.column_mapping):
            value = self.get_file_data(file_data, column["key"])

            # Apply highlighting to the columns that have current_name or new_name
            if column["key"] == "current_name":
                original_name = value
                new_name = file_data.get("new_name", "")
                highlighted_current, _ = highlight_changes(original_name, new_name)
                # Use update_cell to update the current_name cell with highlighted text
                self.update_cell(rel_path, str(column_index), highlighted_current)
            
            elif column["key"] == "new_name":
                original_name = file_data.get("current_name", "")
                new_name = value
                _, highlighted_new = highlight_changes(original_name, new_name)
                # Use update_cell to update the new_name cell with highlighted text
                self.update_cell(rel_path, str(column_index), highlighted_new)
            
            else:
                # For other columns, update the cell without highlighting
                self.update_cell(rel_path, str(column_index), Text(str(value)))

    def old_update_file_row(self, file_data):
        rel_path = file_data["rel_path"]
        if rel_path not in self.rows:
            return
        for column_index, column in enumerate(self.column_mapping):
            print(f"row key {rel_path}, column key {column_index}")
            self.update_cell(rel_path, str(column_index), self.get_file_data(file_data, column["key"]))

    def remove_file_row(self, rel_path: str):
        if rel_path in self.rows:
            self.remove_row(rel_path)

    def handle_file_rename(self, old_rel_path: str, file_data: dict):
        self.remove_file_row(old_rel_path)
        self.add_file_row(file_data)

    def get_file_data(self, file_data, key):
        if key == "is_enabled":
            return "✅" if file_data.get(key, False) else "❌"
        return file_data.get(key, "")

    def update(self, updated_data):
        if "file" in updated_data and "old_name" in updated_data and "new_name" in updated_data:
            file_data = updated_data["file"]
            old_rel_path = updated_data["file"]["rel_path"].replace(file_data["new_name"], updated_data["old_name"])
            self.handle_file_rename(old_rel_path, file_data)
        elif "file" in updated_data:
            self.update_file_row(updated_data["file"])

    def sort_by_column(self, column_index: int):
        """Generic sort handler for any column by index, not by key."""

        def get_sort_key(value):
            real_value = value
            if isinstance(value, Text):
                real_value = value.plain
            # Optional: Custom sort for "is_enabled" column
            if column_index == 0:  # Column 0 is "is_enabled"
                return value == "✅"  # ✅ = True, ❌ = False
            return real_value

        reverse = self.column_sort_order.get(column_index, False)
        self.column_sort_order[column_index] = not reverse

        self.sort(str(column_index), key=get_sort_key, reverse=reverse)


    @on(DataTable.HeaderSelected)
    def on_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Sort the table when the user clicks a column header."""
        self.sort_by_column(event.column_index)

    def get_column_index_by_key(self, key: str) -> int | None:
        """Helper to get column index by column key."""
        for index, column in enumerate(self.column_mapping):
            if column["key"] == key:
                return index
        return None
    

from textual.message import Message

class EditCellRequested(Message):
    def __init__(self, sender: FileTable, row: int, column: int, value: str):
        super().__init__()
        self.sender = sender
        self.row = row
        self.column = column
        self.value = value