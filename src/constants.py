from pathlib import Path

# Technical constants (no language needed)
MIN_BPM = 10
MAX_BPM = 400
SOUND_FILE = str(Path(__file__).parent / "sounds/4c.wav")
SOUND_FILE_UP = str(Path(__file__).parent / "sounds/4d.wav")
SOUND_FILE_SUBDIVISION = str(Path(__file__).parent / "sounds/tripl.wav")
QUIT_COMMAND = "q"
STOP_COMMAND = "s"
EIGHTH_COMMAND = "e"
TRIPLET_COMMAND = "t"
SIXTEENTH_COMMAND = "x"

# Language-specific messages
LANG_EN = {
    "PROMPT_BPM": "Enter BPM (or 'q' to quit, 's' to stop, 'e' for eighth notes, 't' for triplets, 'x' for sixteenth notes, '1-9' for time signature): ",
    "GOODBYE_MSG": "Goodbye!",
    "INVALID_BPM_MSG": f"Please enter a number between {MIN_BPM} and {MAX_BPM}",
    "INVALID_BPM_INIT": f"BPM must be between {MIN_BPM} and {MAX_BPM}",
    "METRONOME_STARTED_MSG": "Metronomnom started. Press 's' to stop.",
    "METRONOME_STOPPED_MSG": "Metronomnom stopped.",
    "NO_SOUND_FILE_MSG": "Metronomnom cannot start without a valid sound file.",
    "COMMAND_ERROR": "You must enter a number or a valid command.",
    "PYMIXER_ERROR": "Error: No audio device found.",
    "0_BPM": "Ah finally, 0 BPM.",
    "TEMPO_CHANGE_MSG": "Tempo changed to {} BPM",
    "DECIMAL_ERROR_MSG": "You must enter a whole number.",
    "NOWAVE_FILE": f"{SOUND_FILE} not found",
    "NOWAVE_FILE_DOWN": f"{SOUND_FILE} (downbeat sound) not found",
    "NOWAVE_FILE_UP": f"{SOUND_FILE_UP} (upbeat sound) not found",
    "NOWAVE_FILE_SUBDIVISION": f"{SOUND_FILE_SUBDIVISION} (subdivision sound) not found",
    "INVALID_MODE": "Invalid mode. Must be normal, eighth, triplet, or sixteenth.",
    "WAV_NOT_LOADED": "Error: Sound files are not loaded.",
    "UI_VALID_BPM": "Current BPM: {}",
    "UI_BEAT_DISPLAY": "Beat: {}",
    "UI_DEFAULT_STATUS": "Enter BPM to start",
    "UI_DEFAULT_BPM": "---",
    "TIME_SIG_CHANGE": "Time signature changed to {}/{}",
    "MODE_EIGHTH": "Switched to eighth notes mode",
    "MODE_TRIPLET": "Switched to triplet mode",
    "MODE_NORMAL": "Switched to normal mode",
    "MODE_CHANGE_STOPPED": "Cannot change mode while metronome is stopped",
    "MODE_SIXTEENTH": "Switched to sixteenth notes mode",
    "TIME_SIG_SET": "Time signature set to {}/{}",
    "TIME_SWITCH": "Time signature set to {}/4",
    "NOT_RUNNING": "Metronomone not running.",
    "PYGAME_INSTALL_MSG": "Please install pygame: pip install pygame",
    "TEXTUAL_ERROR": "Error: Textual library is required for the UI version.",
    "TEXTUAL_INSTALL_MSG": "Please install textual: pip install textual",
    "DEPENDENCY_ERROR": "Cannot start Metronomnom due to missing requirements.",
}

# Current language selection
CURRENT_LANG = LANG_EN