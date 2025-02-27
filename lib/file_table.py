from textual.widgets import DataTable
from lib import DataManager

class FileTable(DataTable):
    def __init__(self, data_manager: DataManager, column_mapping, **kwargs):
        super().__init__(**kwargs)
        self.data_manager = data_manager
        self.column_mapping = column_mapping
        self.initialize_table()

    def initialize_table(self):
        """Initialize the table with columns."""
        self.clear()
        for column in self.column_mapping:
            self.add_column(column["name"])

    def populate_table(self):
        """Full populate (initial load or full refresh)."""
        self.clear()
        for folder_data in self.data_manager.data["folders"].values():
            if not folder_data["is_enabled"]:
                continue
            for file_data in folder_data["files"]:
                if not file_data["is_enabled"]:
                    continue
                self.add_file_row(file_data)

    def add_file_row(self, file_data):
        """Add a new file row, with rel_path as the row key."""
        row = [self.get_file_data(file_data, column["key"]) for column in self.column_mapping]
        self.add_row(*row, key=file_data["rel_path"])

    def update_file_row(self, file_data):
        """Update individual cells for the given file_data using rel_path as key."""
        rel_path = file_data["rel_path"]

        if rel_path not in self.rows:
            # Row doesn't exist (possible if it's filtered out or not loaded yet)
            return

        # Update each column's cell value individually
        for column_index, column in enumerate(self.column_mapping):
            value = self.get_file_data(file_data, column["key"])
            self.update_cell(rel_path, column_index, value)

    # def update_file_row(self, file_data):
    #     """Update an existing row if the file already exists in the table."""
    #     rel_path = file_data["rel_path"]
    #     if rel_path not in self.rows:
    #         # Row doesn't exist (possible if it's a new file, or filtering excluded it)
    #         return

    #     # Build updated row
    #     updated_row = [self.get_file_data(file_data, column["key"]) for column in self.column_mapping]

    #     # Replace row by key (uses rel_path to find the correct row)
    #     self.update_row(rel_path, updated_row)

    def remove_file_row(self, rel_path: str):
        """Remove a row from the table by rel_path."""
        if rel_path in self.rows:
            self.remove_row(rel_path)

    def get_file_data(self, file_data, key):
        """Helper function to get the value for a column."""
        if key == "is_enabled":
            return "✅" if file_data.get(key, False) else "❌"
        return file_data.get(key, "")

