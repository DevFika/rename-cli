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

        undo_count = len(self.data_manager.undo_stack)
        redo_count = len(self.data_manager.redo_stack)
        pending_changes = self.data_manager.get_pending_changes_count()  # Get pending changes count

        self.update(
            f"[bold cyan]Folders:[/bold cyan] [green]Enabled: {amount_of_enabled_folders}[/green] / [yellow]{amount_of_folders}[/yellow]\n"
            f"[bold cyan]Files:[/bold cyan] [green]Enabled: {amount_of_enabled_files}[/green] / [yellow]{amount_of_files}[/yellow]\n"
            f"[red]Undo: {undo_count}[/red] | [blue]Redo: {redo_count}[/blue]\n"
            f"[bold yellow]Pending Changes:[/bold yellow] {pending_changes} / [yellow]{amount_of_files}[/yellow]\n"  # Show pending changes count
        )

    def refresh_display(self):
        """Force a re-update of the info display."""
        self.update_display()
