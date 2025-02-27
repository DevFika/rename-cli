from textual.widgets import Tree
from pathlib import Path
from textual.binding import Binding

from lib import DataManager

# 📂
# ✅☑️🔳🔳☐
ENABLED_FOLDER = f"[green]✅📂[/green]"
DISABLED_FOLDER = f"[red]🔳📂[/red]"
class ToggleTree(Tree[bool]):
    BINDINGS = [
    Binding("a", "toggle_expand_all", "Expand all", show=True,),
    Binding("c", "toggle_collapse_all", "Collapse all", show=True,),
    Binding("x", "disable_all", "Disable all", show=True,),
    Binding("e", "enable_all", "Enable all", show=True),
    Binding("f", "toggle_folder", "Toggle folder", show=True),

    Binding("ctrl+right", "expand_selected_recursive", "Expand selected + children", show=True),
    Binding("ctrl+left", "collapse_selected_recursive", "Collapse selected + children", show=True),
    Binding("ctrl+down", "disable_selected_recursive", "Disable selected + children", show=True),
    Binding("ctrl+up", "enable_selected_recursive", "Enable selected + children", show=True),
    ]

    def __init__(self, data_manager: DataManager, directory_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager
        self.directory_path = directory_path

    def on_mount(self):
        super().on_mount()
        self.root.is_enabled = True
        self.root.path = self.directory_path
        self.border_title = "Folders"
        self.root.expand()

    def toggle_node_state(self, node):
        node.is_enabled = not node.is_enabled
        self.update_node_label(node)
        self.data_manager.update_folder_data(node)
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.prevent_default()
        self.toggle_node_state(event.node)

    def update_node_label(self, node):
        icon = ENABLED_FOLDER if node.is_enabled else DISABLED_FOLDER
        color = "bold green" if node.is_enabled else "bold red"

        node.label = f"{icon} {node.label.plain.split(' ', 1)[1]}"
        node.styles = color

    def action_toggle_expand_all(self):
        self.root.expand_all()

    def action_toggle_collapse_all(self):
        self.root.collapse_all()

    def _set_node_state_recursive(self, node, enable: bool):
        if node.is_enabled != enable:  # Only update if the state is different
            node.is_enabled = enable
            self.update_node_label(node)  # Update label for the current node
            self.data_manager.update_folder_data(node)
        
        # Recurse through all child nodes
        for child in node.children:
            self._set_node_state_recursive(child, enable)

    def action_disable_all(self):
        self.start_batch_update()
        self._set_node_state_recursive(self.root, enable=False)  # Disable all nodes
        self.end_batch_update()
    
    def action_enable_all(self):
        self.start_batch_update()
        self._set_node_state_recursive(self.root, enable=True)  # Enable all nodes
        self.end_batch_update()

    def action_expand_selected_recursive(self):
        node = self.cursor_node
        if node:
            node.expand_all()

    def action_collapse_selected_recursive(self):
        node = self.cursor_node
        if node:
            node.collapse_all()

    def _set_node_state_recursive(self, node, enable: bool):
        if node.is_enabled != enable:
            node.is_enabled = enable
            self.update_node_label(node)
            self.data_manager.update_folder_data(node)
        for child in node.children:
            self._set_node_state_recursive(child, enable)

    def action_enable_selected_recursive(self):
        node = self.cursor_node
        if node:
            self.start_batch_update()
            self._set_node_state_recursive(node, True)
            self.end_batch_update()

    def action_disable_selected_recursive(self):
        node = self.cursor_node
        if node:
            self.start_batch_update()
            self._set_node_state_recursive(node, False)
            self.end_batch_update()

    def action_toggle_folder(self):
        node = self.cursor_node
        if node:
            self.toggle_node_state(node)

    def start_batch_update(self):
        """Start a batch update to suppress UI updates."""
        self.data_manager.start_batch_update()

    def end_batch_update(self):
        """End the batch update and trigger final UI refresh."""
        self.data_manager.end_batch_update()