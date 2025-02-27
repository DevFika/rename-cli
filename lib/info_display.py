from textual.widgets import Static
from lib import DataManager

class InfoDisplay(Static):
    def __init__(self, data_manager: DataManager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager
        self.update_display()

    def update_display(self):
        """Update the content of the InfoDisplay."""
        amount_of_folders = self.data_manager.get_folder_count()
        amount_of_enabled_folders = self.data_manager.get_enabled_folder_count()
        amount_of_files = self.data_manager.get_file_count()
        amount_of_enabled_files = self.data_manager.get_enabled_file_count()

        self.update(
            f"Folders:\n"
            f"  Enabled: {amount_of_enabled_folders} / Total: {amount_of_folders}\n\n"
            f"Files:\n"
            f"  Enabled: {amount_of_enabled_files} / Total: {amount_of_files}"
        )

    def refresh_display(self):
        """Force a re-update of the info display."""
        self.update_display()
