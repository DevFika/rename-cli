from textual.widgets import DataTable, Input, RichLog, Select
from textual.screen import ModalScreen, Screen
from textual.events import Click
from textual.app import ComposeResult
from textual import on
from lib import DataManager
from typing import Any

from .columns import FileTableColumns


class FileTable(DataTable):
    
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.row_metadata = {}
        self.column_sort_order = {}
        self.column_mapping = FileTableColumns.get_all_columns()
        # self.column_mapping = [
        #     {"name": " ", "key": "is_enabled"},
        #     {"name": "Extension", "key": "file_ext"},
        #     {"name": "Current Name", "key": "current_name"},
        #     {"name": "New Name", "key": "new_name"},
        #     {"name": "Size", "key": "size"},
        #     {"name": "Path", "key": "rel_path"},
        #     {"name": "Folder Path", "key": "folder_path"},
        # ]
        self.initialize_table()

    CSS_PATH = "assets/file_table.tcss"

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
        row = [self.get_file_data(file_data, column["key"]) for column in self.column_mapping]
        classes = []
        if not file_data.get("is_enabled"):
            classes.append("disabled")
        if file_data.get("current_name") != file_data.get("new_name"):
            classes.append("pending-change")
        self.add_row(*row, key=file_data["rel_path"])

    def update_file_row(self, file_data):
        rel_path = file_data["rel_path"]
        if rel_path not in self.rows:
            return
        for column_index, column in enumerate(self.column_mapping):
            print(f"row key {rel_path}, column key {column_index}")
            self.update_cell(rel_path, str(column_index), self.get_file_data(file_data, column["key"]))
        # self.update_row_state(rel_path, file_data)

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
            # Optional: Custom sort for "is_enabled" column
            if column_index == 0:  # Column 0 is "is_enabled"
                return value == "✅"  # ✅ = True, ❌ = False
            return value

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
    
    def update_row_state(self, rel_path: str, file_data: dict):
        """Track state and (potentially) apply styling."""
        classes = []
        if not file_data.get("is_enabled", True):
            classes.append("disabled")
        if file_data.get("current_name") != file_data.get("new_name"):
            classes.append("pending-change")

        self.row_metadata[rel_path] = classes
        self.apply_row_styles(rel_path, classes)

    def apply_row_styles(self, rel_path, classes):
        """You can't set row classes directly, so you need to manually apply to each cell."""
        if rel_path not in self.rows:
            return

        # For each cell in the row, update the cell's styles directly (or content if needed)
        row_data = self.get_row(rel_path)

        for column_key, cell_value in row_data.items():
            styled_value = self.apply_cell_styling(cell_value, classes)
            self.update_cell(rel_path, column_key, styled_value)

    
    def apply_cell_styling(self, value, classes):
        """Wrap the value in styled Text or similar (if Textual styles were used)."""
        from textual.widgets import DataTable
        from rich.text import Text

        text = Text(str(value))

        if "disabled" in classes:
            text.stylize("dim")  # Gray out text if disabled
        if "pending-change" in classes:
            text.stylize("bold yellow")  # Highlight for pending changes

        return text
    

from textual.message import Message

class EditCellRequested(Message):
    def __init__(self, sender: FileTable, row: int, column: int, value: str):
        super().__init__()
        self.sender = sender
        self.row = row
        self.column = column
        self.value = value

# class EditCellScreen(ModalScreen):
#     def __init__(
#         self,
#         cell_value: Any,
#         name: str | None = None,
#         id: str | None = None,
#         classes: str | None = None,
#     ) -> None:
#         super().__init__(
#             name=name,
#             id=id,
#             classes=classes,
#         )
#         self.cell_value = cell_value

#     def compose(self) -> ComposeResult:
#         yield Input()

#     def on_mount(self) -> None:
#         cell_input = self.query_one(Input)
#         cell_input.value = str(self.cell_value)

#         cell_input.focus()

#     def on_click(self, event: Click) -> None:
#         clicked, _ = self.get_widget_at(event.screen_x, event.screen_y)
#         # Close the screen if the user clicks outside the modal content
#         # (i.e. the darkened background)
#         if clicked is self:
#             self.app.pop_screen()

#     def on_input_submitted(self, event: Input.Submitted) -> None:
#         main_screen = self.app.get_screen("main")

#         table = main_screen.query_one(DataTable)
#         table.update_cell_at(
#             table.cursor_coordinate,
#             event.value,
#             update_width=True,
#         )

#         message = (
#             f"New value of cell at {table.cursor_coordinate}"
#             f" is {event.value} and type {type(event.value)}"
#         )
#         # main_screen.query_one(RichLog).write(message)

#         self.app.pop_screen()