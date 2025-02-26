# folder_data_manager.py
from pathlib import Path
from typing import Dict

ENABLED_FOLDER = f"[green]■[/green]"
DISABLED_FOLDER = f"[red]■[/red]"

class DataManager:
    def __init__(self, current_directory: Path):
        self.current_directory = current_directory
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

    def update_folder_data(self, node):
        """Update the is_enabled state in the central data structure for the selected folder."""
        folder_data = self.data["folders"].get(str(node.path))

        if folder_data:
            # Update the folder's enabled state
            folder_data["is_enabled"] = node.is_enabled

            # If it's a folder node, update all its files as well
            if Path(node.path).is_dir():  # Check if the node path is a directory
                for file_data in folder_data["files"]:
                    file_data["is_enabled"] = node.is_enabled  # Files are enabled/disabled along with their folder

    def recalculate_summary(self):
        """Recalculate summary data like enabled folder count and total file size."""
        enabled_folders = 0
        enabled_files = 0
        total_size = 0

        for folder_data in self.data["folders"].values():
            if folder_data["is_enabled"]:
                enabled_folders += 1
                for file_data in folder_data["files"]:
                    if file_data["is_enabled"]:
                        enabled_files += 1
                        total_size += file_data["size"]

        self.data["summary"]["enabled_folders_count"] = enabled_folders
        self.data["summary"]["enabled_files_count"] = enabled_files
        self.data["summary"]["total_size"] = total_size

    def populate_tree(self, node, path: Path):
        """Populate the tree structure with folders and files, updating the data dictionary."""
        # Ensure the root directory exists in the data structure
        if str(path) not in self.data["folders"]:
            self.data["folders"][str(path)] = {
                "is_enabled": True,
                "path": str(path),
                "files": []  # Files will be added later
            }

        for child in sorted(path.iterdir()):
            if child.is_dir():
                # Ensure the directory is initialized in the data structure
                folder_data = {
                    "is_enabled": True,
                    "path": str(child),
                    "files": []  # Files will be added later
                }
                self.data["folders"][str(child)] = folder_data
                folder_node = node.add(f"{ENABLED_FOLDER} {child.name}")
                folder_node.data = True  # Initialize data
                folder_node.is_enabled = True
                folder_node.auto_expand = False
                folder_node.path = child
                self.populate_tree(folder_node, child)
            else:
                # Initialize the parent folder in the data structure if not already done
                parent_path = str(child.parent)
                if parent_path not in self.data["folders"]:
                    self.data["folders"][parent_path] = {
                        "is_enabled": True,
                        "path": parent_path,
                        "files": []
                    }

                folder_data = self.data["folders"][parent_path]  # Get parent folder data
                file_data = {
                    "name": child.name,
                    "size": child.stat().st_size,
                    "is_enabled": True,
                    "rel_path": str(child.relative_to(self.current_directory)),
                    "abs_path": str(child)
                }
                folder_data["files"].append(file_data)

    def get_enabled_folders(self, node):
        """Retrieve all enabled folders in the tree."""
        enabled_folders = []
        if node.is_enabled:
            enabled_folders.append(node)
        for child in node.children:
            enabled_folders.extend(self.get_enabled_folders(child))
        return enabled_folders
