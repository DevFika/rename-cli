from typing import Callable
from textual import on
from textual.events import Click
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Input
from textual.containers import Container

class EditCellScreen(ModalScreen):
    CSS_PATH = "../assets/edit_cell_screen.tcss"
    def __init__(self, cell_value: str, on_complete: Callable[[str], None]):
        super().__init__()
        self.cell_value = cell_value
        self.on_complete = on_complete

    def compose(self) -> ComposeResult:
        # with Container(id="modal_container"):
        yield Input(id="edit_cell_input")

    def on_mount(self) -> None:
        cell_input = self.query_one("#edit_cell_input", Input)
        cell_input.value = str(self.cell_value)
        cell_input.focus()

    @on(Click)
    def click(self, event: Click) -> None:
        clicked, _ = self.get_widget_at(event.screen_x, event.screen_y)
        # Close the screen if the user clicks outside the modal content
        if clicked is self:
            self.app.pop_screen()

    @on(Input.Submitted)
    def rename_input_submitted(self, event: Input.Submitted):
        self.on_complete(event.value)
        self.app.pop_screen()