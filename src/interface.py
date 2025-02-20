from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Header, Select
from textual.containers import Horizontal
from textual import on

from constants import CURRENT_LANG, QUIT_COMMAND, STOP_COMMAND
from main import validate_bpm
from metronome import Metronome

# Available time signatures
LINES = """4/4
3/4
2/4
""".splitlines()

class MetroUI(App):
    """A simple Textual-based UI for controlling the metronome."""

    CSS_PATH = "layout.tcss"

    def __init__(self):
        super().__init__()
        self.metronome = None 
        self.beats_per_measure = 4 
        self.beat_unit = 4 

    def compose(self) -> ComposeResult:
        """Defines the UI layout and elements."""
        yield Static("Beat", id="beat", classes="box")
        yield Static("BPM: ---", id="bpm", classes="box")  # Initializes BPM box
        yield Static("Status", id="status", classes="box")

        yield Horizontal(
            Static(CURRENT_LANG["PROMPT_BPM"]),
            Input(placeholder="Type here :)", id="bpm_input", classes="input", type="text", max_length=3),
            Select(((line, line) for line in LINES), value="4/4"),
            classes="input-container"
        )

    @on(Input.Submitted)
    def handle_input(self, event: Input.Submitted) -> None:
        """Handles user input for BPM changes and commands."""
        value = event.value.strip().lower()
        status = self.query_one("#status", Static)
        input_field = self.query_one("#bpm_input", Input)

        if value in {QUIT_COMMAND, STOP_COMMAND}:
            self._handle_stop_or_quit(value, status)
        else:
            self._handle_bpm_change(value, status)

        input_field.value = ""

    @on(Select.Changed)
    def time_change(self, event: Select.Changed) -> None:
        """Handles changes in the selected time signature."""
        beats, unit = event.value.split("/")
        self.beats_per_measure = int(beats)
        self.beat_unit = int(unit)

        if self.metronome:
            self.metronome.beats_per_measure = self.beats_per_measure
            self.metronome.current_beat = 1

        if self.metronome:
            status = self.query_one("#status", Static)
            status.update(CURRENT_LANG["TIME_SIG_CHANGE"].format(beats, unit))

    def update_beat_display(self, beat_number: int) -> None:
        """Update the beat display with the current beat number."""
        beat_display = self.query_one("#beat", Static)
        beat_display.update(str(beat_number))

    def _handle_stop_or_quit(self, value: str, status: Static) -> None:
        """Handles the stop and quit commands."""
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

    def _handle_bpm_change(self, value: str, status: Static) -> None:
        """Validates and applies BPM changes."""
        is_valid, result = validate_bpm(value)

        if is_valid:
            try:
                if self.metronome is None:
                    self.metronome = Metronome(
                        result,
                        on_beat=self.update_beat_display,
                        beats_per_measure=self.beats_per_measure
                    )
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

if __name__ == "__main__":
    app = MetroUI()
    app.run()
