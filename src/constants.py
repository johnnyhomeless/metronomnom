# Technical constants (no language needed)
MIN_BPM = 10
MAX_BPM = 400
SOUND_FILE = "src/sounds/4c.wav"
QUIT_COMMAND = "q"
STOP_COMMAND = "s"

# Language-specific messages
LANG_EN = {
    "PROMPT_BPM": "Enter BPM (or 'q' to quit, 's' to stop): ",
    "GOODBYE_MSG": "Goodbye!",
    "INVALID_BPM_MSG": f"Please enter a number between {MIN_BPM} and {MAX_BPM}",
    "INVALID_BPM_INIT": f"BPM must be between {MIN_BPM} and {MAX_BPM}",
    "METRONOME_STARTED_MSG": "Metronome started. Press 's' to stop.",
    "METRONOME_STOPPED_MSG": "Metronome stopped.",
    "COMMAND_ERROR": "You must enter a number or a valid command.",
    "PYMIXER_ERROR": "Error: No audio device found.",
    "0_BPM": "Ah finally, 0 BPM.",
    "DECIMAL_ERROR_MSG": "You must enter a whole number.",
    "NOWAVE_FILE": f"{SOUND_FILE} not found"
}

# Current language selection
CURRENT_LANG = LANG_EN