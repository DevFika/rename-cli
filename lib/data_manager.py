# folder_data_manager.py
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

ENABLED_FOLDER = f"[green]✅📂[/green]"
DISABLED_FOLDER = f"[red]🔳📂[/red]"

class DataManager:
    def __init__(self, current_directory: Path):
        self.current_directory = current_directory
        self._observers = []
        self.data = {
            "folders": defaultdict(lambda: {"is_enabled": True, "files": []}),
            "summary": {
                "folders_count": 0,
                "enabled_folders_count": 0,
                "files_count": 0,
                "enabled_files_count": 0,
                "total_size": 0,
            }
        }

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, updated_data=None):
        """Notify observers with updated data."""
        for observer in self._observers:
            observer.update(updated_data)


    # --- Data Getters ---
    def get_folder_count(self) -> int:
        """Return the total folder count."""
        return len(self.data["folders"])

    def get_enabled_folder_count(self) -> int:
        """Return the count of enabled folders."""
        return sum(1 for f in self.data["folders"].values() if f["is_enabled"])

    def get_file_count(self) -> int:
        """Return the total file count across all folders."""
        return sum(len(f["files"]) for f in self.data["folders"].values())

    def get_enabled_file_count(self) -> int:
        """Return the count of enabled files."""
        return sum(1 for f in self.data["folders"].values() for file in f["files"] if file["is_enabled"])

    def get_total_size(self) -> int:
        """Return the total size of enabled files."""
        return sum(file["size"] for f in self.data["folders"].values() for file in f["files"] if file["is_enabled"])

    # --- Data Setters ---
    def set_folder_enabled(self, folder_path: str, is_enabled: bool) -> None:
        """Enable or disable a folder."""
        folder_data = self.data["folders"].get(folder_path)
        if folder_data:
            folder_data["is_enabled"] = is_enabled
            # Update all files within the folder
            for file_data in folder_data["files"]:
                file_data["is_enabled"] = is_enabled
            
            self.notify_observers({"folder": folder_data})  # Notify observers

    def set_file_enabled(self, folder_path: str, file_name: str, is_enabled: bool) -> None:
        """Enable or disable a specific file within a folder."""
        folder_data = self.data["folders"].get(folder_path)
        if folder_data:
            file_data = next((f for f in folder_data["files"] if f["name"] == file_name), None)
            if file_data:
                file_data["is_enabled"] = is_enabled
                self.notify_observers({"file": file_data})  # Notify observers

    def set_file_name(self, folder_path: str, old_name: str, new_name: str) -> None:
        """Change the name of a file."""
        folder_data = self.data["folders"].get(folder_path)
        if folder_data:
            file_data = next((f for f in folder_data["files"] if f["name"] == old_name), None)
            if file_data:
                file_data["new_name"] = new_name
                self.notify_observers({"file": file_data, "old_name": old_name, "new_name": new_name})

    def update_folder_data(self, node: Any) -> None:
        """Toggle folder and file states based on node status."""
        folder_data = self.data["folders"].get(str(node.path))
        if folder_data:
            folder_data["is_enabled"] = node.is_enabled
            for file_data in folder_data["files"]:
                file_data["is_enabled"] = node.is_enabled
            self.notify_observers({"folder": folder_data})

    # --- Recalculate Summary ---
    def recalculate_summary(self):
        """Recalculate summary data like enabled folder count and total file size."""
        new_summary = {
            "folders_count": self.get_folder_count(),
            "enabled_folders_count": self.get_enabled_folder_count(),
            "files_count": self.get_file_count(),
            "enabled_files_count": self.get_enabled_file_count(),
            "total_size": self.get_total_size(),
        }
        if new_summary != self.data["summary"]:
            self.data["summary"] = new_summary
            self.notify_observers({"summary": new_summary})  # Only notify if summary changed

    def populate_tree(self, node, path: Path) -> None:
        """Recursively populate the tree with folder and file data."""
        self._add_folder(path)

        for child in sorted(path.iterdir()):
            if child.is_dir():
                folder_node = node.add(f"{ENABLED_FOLDER} {child.name}")
                folder_node.data = True
                folder_node.is_enabled = True
                folder_node.auto_expand = False
                folder_node.path = child
                self.populate_tree(folder_node, child)
            else:
                self._add_file(child)

    def _add_folder(self, path: Path) -> Dict[str, Any]:
        """Ensure a folder exists in the data structure and return its reference."""
        folder_path = str(path)
        return self.data["folders"][folder_path]

    def _add_file(self, file: Path) -> None:
        """Add a file to its parent folder in the data structure."""
        parent_path = str(file.parent)
        file_data = {
            "name": file.name,
            "original_name": file.name,
            "new_name": file.name,
            "size": file.stat().st_size,
            "is_enabled": True,
            "rel_path": str(file.relative_to(self.current_directory)),
            "abs_path": str(file),
        }
        self.data["folders"][parent_path]["files"].append(file_data)

    def get_enabled_folders(self, node):
        """Retrieve all enabled folders in the tree."""
        enabled_folders = []
        if node.is_enabled:
            enabled_folders.append(node)
        for child in node.children:
            enabled_folders.extend(self.get_enabled_folders(child))
        return enabled_folders
