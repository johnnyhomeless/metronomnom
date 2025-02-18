from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.containers import Horizontal
from constants import CURRENT_LANG, QUIT_COMMAND, STOP_COMMAND
from main import validate_bpm
from metronome import Metronome
from textual import on

class MetroUI(App):
    """A simple Textual-based UI for controlling the metronome."""
    
    CSS_PATH = "layout.tcss"

    def __init__(self):
        super().__init__()
        self.metronome = None 

    def compose(self) -> ComposeResult:
        """Defines the UI layout and elements."""
        yield Static("Beat", id="beat", classes="box")
        yield Static("BPM: ---", id="bpm", classes="box")  # Initializes BPM box
        yield Static("Status", id="status", classes="box")
        yield Horizontal(
            Static(CURRENT_LANG["PROMPT_BPM"]),
            Input(placeholder="", id="bpm_input", classes="input", type="text", max_length=3),
            classes="input-container"
        )

    def update_beat_display(self, beat_number: int) -> None:
        """Update the beat display with the current beat number."""
        beat_display = self.query_one("#beat", Static)
        beat_display.update(str(beat_number))

    @on(Input.Submitted)
    def handle_input(self, event: Input.Submitted) -> None:
        """Handles user input for BPM changes and commands."""
        value = event.value.strip().lower()
        status = self.query_one("#status", Static)
        input_field = self.query_one("#bpm_input", Input)

        # Handle quit/stop commands
        if value in {QUIT_COMMAND, STOP_COMMAND}:
            if self.metronome:
                self.metronome.stop()
                self.metronome = None
                status.update(CURRENT_LANG["METRONOME_STOPPED_MSG"])

                # Clear BPM display when stopping
                bpm_display = self.query_one("#bpm", Static)
                bpm_display.update("BPM: ---") 

            if value == QUIT_COMMAND:
                status.update(CURRENT_LANG["GOODBYE_MSG"])
                self.set_timer(2, self.exit)  # Wait 2 seconds before quitting

            input_field.value = ""
            return

        # Validate BPM input
        is_valid, result = validate_bpm(value)
        if is_valid:
            try:
                if self.metronome is None:
                    self.metronome = Metronome(result, on_beat=self.update_beat_display)
                    self.metronome.start()
                    status.update(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} {result} BPM")
                else:
                    self.metronome.update_bpm(result)
                    status.update(CURRENT_LANG["TEMPO_CHANGE_MSG"].format(result))
                
                # Update BPM display
                bpm_display = self.query_one("#bpm", Static)
                bpm_display.update(f"BPM: {result}")

            except FileNotFoundError:
                status.update(CURRENT_LANG["NO_SOUND_FILE_MSG"])
        else:
            status.update(result)  # Display validation error
        
        input_field.value = ""

if __name__ == "__main__":
    app = MetroUI()
    app.run()
