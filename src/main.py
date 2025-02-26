import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from constants import (
    MIN_BPM,
    MAX_BPM,
    QUIT_COMMAND,
    STOP_COMMAND,
    EIGHTH_COMMAND,
    TRIPLET_COMMAND,
    SIXTEENTH_COMMAND,
    CURRENT_LANG
)

from metronome import (
    Metronome,
    EIGHTH_MODE,
    TRIPLET_MODE,
    SIXTEENTH_MODE
)


def validate_bpm(user_input):
    """
    Validate the user's BPM input.
    
    Args:
        user_input (str): The user's input to validate
        
    Returns:
        tuple: (is_valid, result) - Boolean indicating if input is valid and either the BPM or error message
    """
    try:
        float_val = float(user_input)
        
        if not float_val.is_integer():
            return False, CURRENT_LANG["DECIMAL_ERROR_MSG"]
        
        bpm = int(user_input)
        
        if MIN_BPM <= bpm <= MAX_BPM:
            return True, bpm
        
        return False, CURRENT_LANG["INVALID_BPM_MSG"]
    except ValueError:
        return False, CURRENT_LANG["COMMAND_ERROR"]


def handle_quit_or_stop(user_input, metronome_instance):
    """
    Handle quit or stop commands.
    
    Args:
        user_input (str): The user's input
        metronome_instance (Metronome): The current metronome instance
        
    Returns:
        bool: True if quitting, False otherwise
    """
    if metronome_instance:
        metronome_instance.stop()
    
    if user_input == QUIT_COMMAND:
        print(CURRENT_LANG["GOODBYE_MSG"])
        return True
    
    print(CURRENT_LANG["METRONOME_STOPPED_MSG"])
    return False


def handle_rhythm_mode(user_input, metronome_instance):
    """
    Handle rhythm mode change commands.
    
    Args:
        user_input (str): The user's input
        metronome_instance (Metronome): The current metronome instance
    """
    if not metronome_instance:
        print(CURRENT_LANG["MODE_CHANGE_STOPPED"])
        return
    
    if user_input == EIGHTH_COMMAND:
        mode = EIGHTH_MODE
    elif user_input == TRIPLET_COMMAND:
        mode = TRIPLET_MODE
    elif user_input == SIXTEENTH_COMMAND:
        mode = SIXTEENTH_MODE
    else:
        return
    
    current_mode = metronome_instance.set_rhythm_mode(mode)
    print(CURRENT_LANG[f"MODE_{current_mode.upper()}"])


def handle_time_signature(user_input, metronome_instance):
    """
    Handle time signature changes.
    
    Args:
        user_input (str): The user's input (should be a digit 1-9)
        metronome_instance (Metronome): The current metronome instance
        
    Returns:
        bool: True if handled as time signature change, False otherwise
    """
    if not user_input.isdigit() or not (1 <= int(user_input) <= 9):
        return False
    
    beats = int(user_input)
    beat_unit = 4  # Fixed to quarter note
    
    if metronome_instance:
        metronome_instance.beats_per_measure = beats
        metronome_instance.current_beat = 1  # Reset to first beat
        print(CURRENT_LANG["TIME_SIG_CHANGE"].format(beats, beat_unit))
    else:
        print(f"Time signature set to {beats}/4")
    
    return True


def handle_bpm_update(user_input, metronome_instance):
    """
    Handle BPM validation and updates.
    
    Args:
        user_input (str): The user's input
        metronome_instance (Metronome): The current metronome instance
        
    Returns:
        Metronome: Updated or new metronome instance, or None if invalid
    """
    is_valid, result = validate_bpm(user_input)
    
    if is_valid:
        if metronome_instance is None:
            metronome_instance = Metronome(result)
            metronome_instance.start()
            print(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} {result} BPM")
        else:
            metronome_instance.update_bpm(result)
        return metronome_instance
    else:
        print(result)
        return metronome_instance


def run_metronome():
    """
    Main function to run the metronome CLI interface.
    """
    metronome_instance = None
    
    # Display initial instructions
    print("Welcome to Metronomnom!")
    print("Use 1-9 keys to set time signature (e.g., '3' for 3/4 time)")

    try:
        while True:
            user_input = input(CURRENT_LANG["PROMPT_BPM"]).strip().lower()
            
            # Handle quit/stop commands
            if user_input in {QUIT_COMMAND, STOP_COMMAND}:
                should_quit = handle_quit_or_stop(user_input, metronome_instance)
                metronome_instance = None
                if should_quit:
                    break
                continue
            
            # Handle rhythm mode commands
            elif user_input in {EIGHTH_COMMAND, TRIPLET_COMMAND, SIXTEENTH_COMMAND}:
                handle_rhythm_mode(user_input, metronome_instance)
                continue
            
            # Handle special case for 0 BPM
            elif user_input == "0":
                print(CURRENT_LANG["0_BPM"])
                continue
            
            # Handle time signature changes (1-9)
            elif handle_time_signature(user_input, metronome_instance):
                continue
            
            # Handle BPM changes
            metronome_instance = handle_bpm_update(user_input, metronome_instance)
    
    except KeyboardInterrupt:
        if metronome_instance:
            metronome_instance.stop()
        
        print("\n" + CURRENT_LANG["GOODBYE_MSG"])


if __name__ == "__main__":
    run_metronome()