from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Horizontal
from textual import on
import time

# Import constants for commands and language settings
from constants import (
    CURRENT_LANG, 
    QUIT_COMMAND, 
    STOP_COMMAND,
    EIGHTH_COMMAND,
    TRIPLET_COMMAND,
    SIXTEENTH_COMMAND  
)
from main import validate_bpm, check_dependencies
from metronome import (
    Metronome,
    EIGHTH_MODE,
    TRIPLET_MODE,
    SIXTEENTH_MODE  
)

#=====================================================
# Main UI Application Class
#=====================================================

class MetroUI(App):
    """
    A Textual-based UI for controlling the metronome.
    Provides a simple text-based interface for adjusting BPM, 
    changing time signatures, and switching rhythm modes.
    
    Features:
    - Visual beat counter display
    - BPM input and display
    - Time signature control (using number keys 1-9)
    - Status updates and feedback
    - Command-based interface for mode switching
    """

    CSS_PATH = "layout.tcss"  # Path to the stylesheet that controls appearance

    def __init__(self):
        """Initialize the MetroUI application with default settings."""
        super().__init__()
        self.metronome = None  # Will hold the metronome instance when running
        self.beats_per_measure = 4  # Default time signature: 4/4
        self.beat_unit = 4  # Quarter note beat unit (fixed for now)
        
        # Tap tempo variables
        self.tap_times = []  # Store timestamps of taps
        self.max_tap_age = 5.0  # Reset taps after 5 seconds of inactivity
        self.min_taps_required = 2  # Need at least 2 taps to calculate tempo

    #-----------------------------------------------------
    # UI Layout Definition
    #-----------------------------------------------------

    def compose(self) -> ComposeResult:
        """
        Define the UI layout and elements.
        
        The layout consists of:
        - Beat display (shows current beat number)
        - BPM display (shows current tempo)
        - Time signature display
        - Status message area
        - Command input field
        
        Returns:
            ComposeResult: The composed UI elements
        """
        # Display widgets showing metronome state
        yield Static("Beat", id="beat", classes="box")          # Current beat indicator
        yield Static("BPM: ---", id="bpm", classes="box")       # Tempo display
        yield Static(f"{self.beats_per_measure}/4", id="time_sig", classes="box")  # Time signature display
        yield Static("Welcome to Metronomnom :)", id="status", classes="box")  # Status messages

        # Input container for user commands
        yield Horizontal(
            Static(CURRENT_LANG["PROMPT_BPM"]),                 # Input prompt text
            Input(placeholder="Type here :)", id="bpm_input", classes="input", type="text", max_length=3),  # Command input field
            Button("Tap", id="tap_button"),
            classes="input-container"
        )

    #-----------------------------------------------------
    # Input Handling
    #-----------------------------------------------------

    @on(Input.Submitted)  # Event handler for when user submits input
    def handle_input(self, event: Input.Submitted) -> None:
        """
        Process user input to control the metronome.
        
        Handles:
        - BPM changes (numeric input)
        - Stop/quit commands
        - Rhythm mode changes (e/t/x commands)
        - Time signature changes (1-9)
        
        Args:
            event (Input.Submitted): The input submission event
        """
        value = event.value.strip().lower()  # Normalize the input
        status = self.query_one("#status", Static)  # Get status display widget
        input_field = self.query_one("#bpm_input", Input)  # Get input field

        # Route the input to the appropriate handler based on content
        if value in {QUIT_COMMAND, STOP_COMMAND}:
            # Handle metronome stopping and app quitting
            self._handle_stop_or_quit(value, status)
        
        elif value in {EIGHTH_COMMAND, TRIPLET_COMMAND, SIXTEENTH_COMMAND}:
            # Handle rhythm subdivision mode changes
            self._handle_mode_change(value, status)
        
        elif value.isdigit() and 1 <= int(value) <= 9:
            # Handle time signature changes using number keys
            self._handle_time_signature_change(int(value), status)
        
        else:
            # Treat as potential BPM change
            self._handle_bpm_change(value, status)

        # Clear input field after processing
        input_field.value = ""

    #-----------------------------------------------------
    # Handler Methods for Different Commands
    #-----------------------------------------------------

    def _handle_time_signature_change(self, beats: int, status: Static) -> None:
        """
        Change the time signature (number of beats per measure).
        
        Args:
            beats (int): The number of beats per measure (1-9)
            status (Static): The status display widget for feedback
        """
        # Update our local state
        self.beats_per_measure = beats
        self.beat_unit = 4  # Stays fixed at quarter note for now
        
        # Update the time signature display in the UI
        time_sig_display = self.query_one("#time_sig", Static)
        time_sig_display.update(f"{self.beats_per_measure}/4")
        
        # Update the metronome if it's running, otherwise just show message
        if self.metronome:
            self.metronome.beats_per_measure = self.beats_per_measure
            self.metronome.current_beat = 1  # Reset to first beat
            status.update(CURRENT_LANG["TIME_SIG_CHANGE"].format(beats, self.beat_unit))
        else:
            status.update(CURRENT_LANG["TIME_SWITCH"].format(beats))

    def _handle_mode_change(self, value: str, status: Static) -> None:
        """
        Switch between different rhythm modes (eighth notes, triplets, sixteenth notes).
        
        Args:
            value (str): The command character for the desired mode
            status (Static): The status display widget for feedback
        """
        # Cannot change mode if metronome isn't running
        if not self.metronome:
            status.update(CURRENT_LANG["MODE_CHANGE_STOPPED"])
            return
        
        # Map command characters to their corresponding modes
        mode_map = {
            EIGHTH_COMMAND: EIGHTH_MODE,      # 'e' for eighth notes
            TRIPLET_COMMAND: TRIPLET_MODE,    # 't' for triplets
            SIXTEENTH_COMMAND: SIXTEENTH_MODE,  # 'x' for sixteenth notes
        }
        
        # Set the new mode and show feedback
        mode = mode_map.get(value)
        if mode:
            current_mode = self.metronome.set_rhythm_mode(mode)
            status.update(CURRENT_LANG[f"MODE_{current_mode.upper()}"])

    def _handle_bpm_change(self, value: str, status: Static) -> None:
        """
        Validate and apply BPM changes.
        
        Args:
            value (str): The input BPM value to set
            status (Static): The status display widget for feedback
        """
        # Validate the BPM value
        is_valid, result = validate_bpm(value)

        if is_valid:
            # Either create a new metronome or update existing one
            if self.metronome is None:
                self._create_and_start_metronome(result, status)
            else:
                self.metronome.update_bpm(result)
                status.update(CURRENT_LANG["TEMPO_CHANGE_MSG"].format(result))
            
            # Update the BPM display
            bpm_display = self.query_one("#bpm", Static)
            bpm_display.update(f"BPM: {result}")
        else:
            # Show validation error message
            status.update(result)

    def _create_and_start_metronome(self, bpm: int, status: Static) -> None:
        """
        Create and start a new metronome instance.
        
        Args:
            bpm (int): The initial BPM for the metronome
            status (Static): The status display widget for feedback
        """
        # Create metronome with callback to update beat display
        self.metronome = Metronome(
            bpm,
            on_beat=self.update_beat_display,  # This will update the UI on each beat
            beats_per_measure=self.beats_per_measure
        )
        self.metronome.start()
        status.update(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} {bpm} BPM")

    def _handle_stop_or_quit(self, value: str, status: Static) -> None:
        """
        Handle stopping the metronome and/or quitting the application.
        
        Args:
            value (str): The command ('q' for quit, 's' for stop)
            status (Static): The status display widget for feedback
        """
        # Stop the metronome if it's running
        if self.metronome:
            self.metronome.stop()
            self.metronome = None
            status.update(CURRENT_LANG["METRONOME_STOPPED_MSG"])
            
            # Reset the BPM display when stopped
            self.query_one("#bpm", Static).update("BPM: ---")

        # Handle quit command with a delayed exit
        if value == QUIT_COMMAND:
            status.update(CURRENT_LANG["GOODBYE_MSG"])
            self.set_timer(2, self.exit)  # Wait 2 seconds before quitting

    #-----------------------------------------------------
    # UI Update Methods
    #-----------------------------------------------------

    def update_beat_display(self, beat_number: int) -> None:
        """
        Update the UI to show the current beat number.
        Called by metronome on each beat.
        
        Args:
            beat_number (int): The current beat in the measure
        """
        self.query_one("#beat", Static).update(str(beat_number))

    @on(Button.Pressed, "#tap_button")
    def handle_tap(self, event: Button.Pressed) -> None:
        """
        Handle tap button presses to calculate tempo based on tap rhythm.
        
        Args:
            event (Button.Pressed): The button press event
        """
        current_time = time.time()
        status = self.query_one("#status", Static)
        
        # Remove old taps (older than max_tap_age seconds)
        self.tap_times = [t for t in self.tap_times if current_time - t < self.max_tap_age]
        
        # Add the new tap
        self.tap_times.append(current_time)
        
        # Calculate BPM if we have enough taps
        if len(self.tap_times) >= self.min_taps_required:
            bpm = self.calculate_tap_tempo()
            
            # Put the calculated BPM in the input field for confirmation
            input_field = self.query_one("#bpm_input", Input)
            input_field.value = str(bpm)
            
            # Focus the input field so the user can just press Enter
            input_field.focus()
            
            # Update BPM display for visual feedback
            bpm_display = self.query_one("#bpm", Static)
            bpm_display.update(f"BPM: {bpm}")

    # Add this method to calculate BPM from tap timestamps
    def calculate_tap_tempo(self) -> int:
        """
        Calculate BPM based on the time between taps.

        Returns:
            int: The calculated BPM, clamped to valid range
        """
        # Calculate time intervals between taps
        intervals = [self.tap_times[i] - self.tap_times[i-1] for i in range(1, len(self.tap_times))]
       
        # Prevent division by zero
        if not intervals: 
            return MIN_BPM
         
        # Calculate average interval
        avg_interval = sum(intervals) / len(intervals)

        # Convert to BPM (60 seconds / average interval)
        bpm = int(60 / avg_interval)

        # Clamp to valid BPM range (using constants from constants.py)
        from constants import MIN_BPM, MAX_BPM
        bpm = max(MIN_BPM, min(bpm, MAX_BPM))

        return bpm

# Entry point - create and run the application
if __name__ == "__main__":
    if check_dependencies(check_textual=1):
        app = MetroUI()
        app.run()
    else:
        print(CURRENT_LANG["DEPENDENCY_ERROR"])