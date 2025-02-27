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
        self.batch_update_mode = False

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, updated_data=None):
        """Notify observers with updated data if not in batch update mode."""
        if not self.batch_update_mode:
            for observer in self._observers:
                observer.update(updated_data)

    def start_batch_update(self):
        """Call this method to start a batch update."""
        self.batch_update_mode = True

    def end_batch_update(self):
        """Call this method to end a batch update and notify observers."""
        self.batch_update_mode = False
        self.recalculate_summary()
        self.notify_observers({"batch_update_done": True})


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
        """Return the count of enabled files, considering folder enabled state."""
        return sum(1 for f in self.data["folders"].values() if f["is_enabled"] 
                for file in f["files"] if file["is_enabled"])

    def get_total_size(self) -> int:
        """Return the total size of enabled files, considering folder enabled state."""
        return sum(file["size"] for f in self.data["folders"].values() if f["is_enabled"]
                for file in f["files"] if file["is_enabled"])


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
            self.recalculate_summary(updated_data={"folder": folder_data})
    
    def toggle_file_enabled(self, folder_path: str, file_name: str) -> None:
        """Toggle the 'is_enabled' status of a specific file within a folder."""
        folder_data = self.data["folders"].get(folder_path)
        if folder_data:
            file_data = next((f for f in folder_data["files"] if f["name"] == file_name), None)
            if file_data:
                file_data["is_enabled"] = not file_data["is_enabled"]
                self.notify_observers({"file": file_data})
                self.recalculate_summary(updated_data={"file": file_data})


    def set_file_enabled(self, folder_path: str, file_name: str, is_enabled: bool) -> None:
        """Enable or disable a specific file within a folder."""
        folder_data = self.data["folders"].get(folder_path)
        if folder_data:
            file_data = next((f for f in folder_data["files"] if f["name"] == file_name), None)
            if file_data:
                file_data["is_enabled"] = is_enabled
                self.notify_observers({"file": file_data})  # Notify observers
                self.recalculate_summary(updated_data={"file": file_data})

    def set_file_name(self, folder_path: str, old_name: str, new_name: str) -> None:
        """Change the name of a file."""
        print(self.data)
        folder_data = self.data["folders"].get(folder_path)
        print(folder_data)
        if folder_data:
            file_data = next((f for f in folder_data["files"] if f["name"] == old_name), None)
            print(file_data)
            if file_data:
                file_data["new_name"] = new_name
                print(f"file: {file_data}, old_name: {old_name}, new_name: {new_name}")
                self.notify_observers({"file": file_data, "old_name": old_name, "new_name": new_name})
                self.recalculate_summary(updated_data={"file": file_data})
    
    def update_folder_data(self, node: Any) -> None:
        """Toggle folder and file states based on node status."""
        folder_data = self.data["folders"].get(str(node.path))
        if folder_data:
            folder_data["is_enabled"] = node.is_enabled
            for file_data in folder_data["files"]:
                file_data["is_enabled"] = node.is_enabled
            self.notify_observers({"folder": folder_data})
            self.recalculate_summary(updated_data={"folder": folder_data})

    def recalculate_summary(self, updated_data=None):
        """Recalculate summary data like enabled folder count and total file size."""
        
        # If we don't have updated data, we will perform a full recalculation
        if not updated_data:
            new_summary = {
                "folders_count": self.get_folder_count(),
                "enabled_folders_count": self.get_enabled_folder_count(),
                "files_count": self.get_file_count(),
                "enabled_files_count": self.get_enabled_file_count(),
                "total_size": self.get_total_size(),
            }
            self.data["summary"] = new_summary
            self.notify_observers({"summary": new_summary})  # Always notify if recalculated

            return

        # If we have updated data, only update parts of the summary that changed
        new_summary = self.data["summary"].copy()

        if "folder" in updated_data:
            folder_data = updated_data["folder"]
            if "is_enabled" in folder_data:
                if folder_data["is_enabled"]:
                    new_summary["enabled_folders_count"] += 1
                else:
                    new_summary["enabled_folders_count"] -= 1

        if "file" in updated_data:
            file_data = updated_data["file"]
            if "is_enabled" in file_data:
                if file_data["is_enabled"]:
                    new_summary["enabled_files_count"] += 1
                    new_summary["total_size"] += file_data["size"]
                else:
                    new_summary["enabled_files_count"] -= 1
                    new_summary["total_size"] -= file_data["size"]

        if new_summary != self.data["summary"]:
            self.data["summary"] = new_summary
            self.notify_observers({"summary": new_summary})  # Only notify if summary changed


    def populate_tree(self, node, path: Path, recursive: bool = True) -> None:
        """Recursively populate the tree with folder and file data."""
        self._add_folder(path)

        for child in sorted(path.iterdir()):
            if child.is_dir():
                folder_icon = ENABLED_FOLDER if recursive else DISABLED_FOLDER
                folder_node = node.add(f"{folder_icon} {child.name}")
                folder_node.data = True
                folder_node.auto_expand = False
                folder_node.path = child

                folder_data = self.data["folders"][str(child)]
                folder_data["is_enabled"] = recursive  # Set based on the recursive flag

                if recursive:
                    folder_node.is_enabled = True
                else:
                    folder_node.is_enabled = False
                
                self.populate_tree(folder_node, child, recursive)
            else:
                self._add_file(child)
        self.recalculate_summary()

    def _add_folder(self, path: Path) -> Dict[str, Any]:
        """Ensure a folder exists in the data structure and return its reference."""
        folder_path = str(path)
        return self.data["folders"][folder_path]

    def _add_file(self, file: Path) -> None:
        """Add a file to its parent folder in the data structure."""
        parent_path = str(file.parent)
        file_data = {
            "name": file.name,
            "current_name": file.name,
            "new_name": file.name,
            "size": file.stat().st_size,
            "is_enabled": True,
            "rel_path": str(file.relative_to(self.current_directory)),
            "abs_path": str(file),
            "file_ext": ".temp",
            "folder_path": parent_path,
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

    def is_folder_enabled(self, file_abs_path: str) -> bool:
        """Check if the folder containing the given file is enabled."""
        folder_path = str(Path(file_abs_path).parent)
        folder_data = self.data["folders"].get(folder_path)
        if folder_data is None:
            # If folder isn't explicitly tracked, assume disabled (or you could assume enabled if needed)
            return False
        return folder_data["is_enabled"]
