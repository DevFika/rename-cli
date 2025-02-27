from textual.widgets import DataTable
from textual import on
from lib import DataManager

class FileTable(DataTable):
    def __init__(self, data_manager: DataManager, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager

        self.column_mapping = [
            {"name": " ", "key": "is_enabled"},
            {"name": "Extension", "key": "file_ext"},
            {"name": "Current Name", "key": "current_name"},
            {"name": "New Name", "key": "new_name"},
            {"name": "Size", "key": "size"},
            {"name": "Path", "key": "rel_path"},
            {"name": "Folder Path", "key": "folder_path"},
        ]
        self.initialize_table()


    @on(DataTable.CellSelected)
    def data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        # Extracting the cell value
        cell_value = event.value
        message = (
            f"Original value of cell at {event.coordinate}"
            f" is {event.value} and type {type(event.value)}"
        )

        rel_path_column_index = next(
            (index for index, col in enumerate(self.column_mapping) if col["key"] == "rel_path"),
            None
        )
        is_enabled_index = next(
            (index for index, col in enumerate(self.column_mapping) if col["key"] == "is_enabled"),
            None
        )
        current_name_index = next(
            (index for index, col in enumerate(self.column_mapping) if col["key"] == "current_name"),
            None
        )
        folder_path_column_index = next(
            (index for index, col in enumerate(self.column_mapping) if col["key"] == "folder_path"),
            None
        )

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

        if event.coordinate.column == is_enabled_index:
            print("Lets toggle file")
            self.data_manager.toggle_file_enabled(folder_value, current_name_value)

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
                if not file_data["is_enabled"]:
                    continue
                self.add_file_row(file_data)

    def add_file_row(self, file_data):
        row = [self.get_file_data(file_data, column["key"]) for column in self.column_mapping]
        self.add_row(*row, key=file_data["rel_path"])

    def update_file_row(self, file_data):
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
