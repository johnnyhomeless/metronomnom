from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Header
from textual.containers import Horizontal
from textual import on

from constants import (
    CURRENT_LANG, 
    QUIT_COMMAND, 
    STOP_COMMAND,
    EIGHTH_COMMAND,
    TRIPLET_COMMAND,
    SIXTEENTH_COMMAND  
)
from main import validate_bpm
from metronome import (
    Metronome,
    EIGHTH_MODE,
    TRIPLET_MODE,
    SIXTEENTH_MODE  
)


class MetroUI(App):
    """
    A Textual-based UI for controlling the metronome.
    Provides visual interface with BPM control and rhythm mode switching.
    Time signatures can be changed using number keys (1-9).
    """

    CSS_PATH = "layout.tcss"

    def __init__(self):
        """Initialize the MetroUI application."""
        super().__init__()
        self.metronome = None 
        self.beats_per_measure = 4 
        self.beat_unit = 4 

    def compose(self) -> ComposeResult:
        """
        Define the UI layout and elements.
        
        Returns:
            ComposeResult: The composed UI elements
        """
        yield Static("Beat", id="beat", classes="box")
        yield Static("BPM: ---", id="bpm", classes="box")
        yield Static(f"Time Sig: {self.beats_per_measure}/4", id="time_sig", classes="box")
        yield Static("Welcome to Metronomnom :)", id="status", classes="box")

        yield Horizontal(
            Static(CURRENT_LANG["PROMPT_BPM"]),
            Input(placeholder="Type here :)", id="bpm_input", classes="input", type="text", max_length=3),
            classes="input-container"
        )

    @on(Input.Submitted)
    def handle_input(self, event: Input.Submitted) -> None:
        """
        Handle user input for BPM changes and commands.
        
        Args:
            event (Input.Submitted): The input submission event
        """
        value = event.value.strip().lower()
        status = self.query_one("#status", Static)
        input_field = self.query_one("#bpm_input", Input)

        # Handle stop/quit commands
        if value in {QUIT_COMMAND, STOP_COMMAND}:
            self._handle_stop_or_quit(value, status)
        
        # Handle rhythm mode commands
        elif value in {EIGHTH_COMMAND, TRIPLET_COMMAND, SIXTEENTH_COMMAND}:
            self._handle_mode_change(value, status)
        
        # Handle time signature changes (1-9 for beats per measure)
        elif value.isdigit() and 1 <= int(value) <= 9:
            self._handle_time_signature_change(int(value), status)
        
        # Handle BPM changes
        else:
            self._handle_bpm_change(value, status)

        input_field.value = ""

    def _handle_time_signature_change(self, beats: int, status: Static) -> None:
        """
        Handle time signature changes.
        
        Args:
            beats (int): The number of beats per measure
            status (Static): The status display widget
        """
        self.beats_per_measure = beats
        self.beat_unit = 4  # Fixed to quarter note for now
        
        # Update time signature display
        time_sig_display = self.query_one("#time_sig", Static)
        time_sig_display.update(f"Time Sig: {self.beats_per_measure}/4")
        
        # Update metronome if running
        if self.metronome:
            self.metronome.beats_per_measure = self.beats_per_measure
            self.metronome.current_beat = 1  # Reset to first beat
            status.update(CURRENT_LANG["TIME_SIG_CHANGE"].format(beats, self.beat_unit))
        else:
            status.update(f"Time signature set to {beats}/4")

    def _handle_mode_change(self, value: str, status: Static) -> None:
        """
        Handle rhythm mode changes.
        
        Args:
            value (str): The command value for mode change
            status (Static): The status display widget
        """
        if not self.metronome:
            status.update(CURRENT_LANG["MODE_CHANGE_STOPPED"])
            return
            
        if value == EIGHTH_COMMAND:
            mode = EIGHTH_MODE
        elif value == TRIPLET_COMMAND:
            mode = TRIPLET_MODE
        elif value == SIXTEENTH_COMMAND:
            mode = SIXTEENTH_MODE
        else:
            return
        
        current_mode = self.metronome.set_rhythm_mode(mode)
        status.update(CURRENT_LANG[f"MODE_{current_mode.upper()}"])

    def _handle_bpm_change(self, value: str, status: Static) -> None:
        """
        Validate and apply BPM changes.
        
        Args:
            value (str): The input BPM value
            status (Static): The status display widget
        """
        is_valid, result = validate_bpm(value)

        if is_valid:
            try:
                if self.metronome is None:
                    self._create_and_start_metronome(result, status)
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

    def _create_and_start_metronome(self, bpm: int, status: Static) -> None:
        """
        Create and start a new metronome instance.
        
        Args:
            bpm (int): The BPM to use
            status (Static): The status display widget
        """
        self.metronome = Metronome(
            bpm,
            on_beat=self.update_beat_display,
            beats_per_measure=self.beats_per_measure
        )
        self.metronome.start()
        status.update(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} {bpm} BPM")

    def _handle_stop_or_quit(self, value: str, status: Static) -> None:
        """
        Handle stop and quit commands.
        
        Args:
            value (str): The command value
            status (Static): The status display widget
        """
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

    def update_beat_display(self, beat_number: int) -> None:
        """
        Update the beat display with the current beat number.
        
        Args:
            beat_number (int): The current beat number
        """
        beat_display = self.query_one("#beat", Static)
        beat_display.update(str(beat_number))


if __name__ == "__main__":
    app = MetroUI()
    app.run()