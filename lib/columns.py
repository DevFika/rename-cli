from enum import Enum

class FileTableColumns(Enum):
    EXTENSION = {"name": "Extension", "key": "file_ext"}
    IS_ENABLED = {"name": " ", "key": "is_enabled"}
    CURRENT_NAME = {"name": "Current Name", "key": "current_name"}
    NEW_NAME = {"name": "New Name", "key": "new_name"}
    SIZE = {"name": "Size", "key": "size"}
    REL_PATH = {"name": "Path", "key": "rel_path"}
    FOLDER_PATH = {"name": "Folder Path", "key": "folder_path"}

    @classmethod
    def get_column_name(cls, column_key):
        """Get column name based on its key."""
        for column in cls:
            if column.value["key"] == column_key:
                return column.value["name"]
        return None  # If no match is found

    @classmethod
    def get_column_index(cls, column_key):
        """Retrieve the index of a column based on its key."""
        column_mapping = cls.get_all_columns()
        for index, column in enumerate(column_mapping):
            if column["key"] == column_key:
                return index
        return -1  # If no match is found

    @classmethod
    def get_all_columns(cls):
        """Return all column names and keys as a list of dictionaries."""
        return [column.value for column in cls]
