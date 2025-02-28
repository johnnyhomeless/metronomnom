# main.py
import os
# Suppress Pygame's welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  

#=======================================================
# Imports
#=======================================================

# Import constants for BPM limits, commands, and language settings
from constants import (
    MIN_BPM, MAX_BPM, QUIT_COMMAND, STOP_COMMAND,
    EIGHTH_COMMAND, TRIPLET_COMMAND, SIXTEENTH_COMMAND, CURRENT_LANG
)

# Import the Metronome class and rhythm mode constants
from metronome import (
    Metronome, EIGHTH_MODE, TRIPLET_MODE, SIXTEENTH_MODE
)

#=======================================================
# Input Validation Functions
#=======================================================

def validate_bpm(user_input):
    """
    Validate the BPM input to ensure it is a valid integer within the allowed range.
    
    Args:
        user_input (str): The user's input string to be validated.
    
    Returns:
        tuple: (is_valid, result) - Boolean indicating validity, and either the BPM or an error message.
    """
    try:
        # First, convert to float to handle potential decimal input
        float_val = float(user_input)
        
        # Reject non-integer values (e.g., decimals)
        if not float_val.is_integer():
            return False, CURRENT_LANG["DECIMAL_ERROR_MSG"]
        
        # Convert to integer for comparison
        bpm = int(user_input)
        
        # Check if BPM is within the valid range
        if MIN_BPM <= bpm <= MAX_BPM:
            return True, bpm
        
        # BPM is out of valid range
        return False, CURRENT_LANG["INVALID_BPM_MSG"]
    except ValueError:
        # Input couldn't be converted to a number
        return False, CURRENT_LANG["COMMAND_ERROR"]

#=======================================================
# Command Handler Functions
#=======================================================

def handle_quit_or_stop(user_input, metronome_instance):
    """
    Handle the quit or stop commands to control the metronome.
    
    Args:
        user_input (str): The command entered by the user.
        metronome_instance (Metronome): The active metronome instance.
    
    Returns:
        bool: True if the program should exit, False otherwise.
    """
    # Stop the metronome if it exists
    if metronome_instance:
        metronome_instance.stop()
    
    # Handle quit command
    if user_input == QUIT_COMMAND:
        print(CURRENT_LANG["GOODBYE_MSG"])
        return True  # Signal to exit the program
    
    # Handle stop command
    elif user_input == STOP_COMMAND: 
        if metronome_instance:
            # Only show "stopped" message if metronome was actually running
            print(CURRENT_LANG["METRONOME_STOPPED_MSG"])
        else:
            # Inform user if they try to stop a metronome that isn't running
            print(CURRENT_LANG["NOT_RUNNING"])
    
    return False  # Continue running the program

def handle_rhythm_mode(user_input, metronome_instance):
    """
    Change the rhythm mode of the metronome (eighth notes, triplets, sixteenth notes).
    
    Args:
        user_input (str): The command entered by the user.
        metronome_instance (Metronome): The active metronome instance.
    """
    # Cannot change mode if metronome isn't running
    if not metronome_instance:
        print(CURRENT_LANG["MODE_CHANGE_STOPPED"])
        return
    
    # Determine the rhythm mode based on user input
    if user_input == EIGHTH_COMMAND:
        mode = EIGHTH_MODE        # Two subdivisions per beat
    elif user_input == TRIPLET_COMMAND:
        mode = TRIPLET_MODE       # Three subdivisions per beat
    elif user_input == SIXTEENTH_COMMAND:
        mode = SIXTEENTH_MODE     # Four subdivisions per beat
    else:
        return  # Unrecognized mode command
    
    # Apply the mode change and show feedback message
    current_mode = metronome_instance.set_rhythm_mode(mode)
    print(CURRENT_LANG[f"MODE_{current_mode.upper()}"])

def handle_time_signature(user_input, metronome_instance):
    """
    Handle changes to the time signature.
    
    Args:
        user_input (str): The user input representing the number of beats per measure (1-9).
        metronome_instance (Metronome): The active metronome instance.
    
    Returns:
        bool: True if the time signature was changed, False otherwise.
    """
    # Check if input is a valid time signature (1-9)
    if not user_input.isdigit() or not (1 <= int(user_input) <= 9):
        return False
    
    # Convert to integer and set beat unit (always quarter note for now)
    beats = int(user_input)
    beat_unit = 4  # The beat unit remains a quarter note
    
    # Apply the time signature change
    if metronome_instance:
        # Update running metronome
        metronome_instance.beats_per_measure = beats
        metronome_instance.current_beat = 1  # Reset to first beat
        print(CURRENT_LANG["TIME_SIG_CHANGE"].format(beats, beat_unit))
    else:
        # Just show message if metronome isn't running
        print(CURRENT_LANG["TIME_SWITCH"].format(beats))
    
    return True  # Signal that we handled a time signature change

def handle_bpm_update(user_input, metronome_instance):
    """
    Validate and update the BPM of the metronome.
    
    Args:
        user_input (str): The BPM entered by the user.
        metronome_instance (Metronome): The active metronome instance.
    
    Returns:
        Metronome: The updated or newly created metronome instance.
    """
    # Validate the input BPM
    is_valid, result = validate_bpm(user_input)
    
    if is_valid:
        if metronome_instance is None:
            # Create and start a new metronome
            metronome_instance = Metronome(result)
            metronome_instance.start()
            print(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} {result} BPM")
        else:
            # Update existing metronome
            metronome_instance.update_bpm(result)
        return metronome_instance
    else:
        # Show validation error and return unchanged instance
        print(result)
        return metronome_instance

#=======================================================
# Main Program Function
#=======================================================

def run_metronome():
    """
    Start the metronome CLI and handle user interactions.
    This is the main loop of the command-line interface.
    """
    metronome_instance = None  # No active metronome at start
    
    # Display startup instructions
    print("Welcome to Metronomnom!")
    print("Use 1-9 keys to set time signature (e.g., '3' for 3/4 time)")
    
    try:
        # Main command processing loop
        while True:
            # Get user input, strip whitespace, convert to lowercase
            user_input = input(CURRENT_LANG["PROMPT_BPM"]).strip().lower()
            
            # Handle different types of commands
            
            # 1. Handle quitting or stopping the metronome
            if user_input in {QUIT_COMMAND, STOP_COMMAND}:
                should_quit = handle_quit_or_stop(user_input, metronome_instance)
                metronome_instance = None  # Clear reference to stopped metronome
                if should_quit:
                    break  # Exit the program loop
                continue
            
            # 2. Handle rhythm mode changes
            elif user_input in {EIGHTH_COMMAND, TRIPLET_COMMAND, SIXTEENTH_COMMAND}:
                handle_rhythm_mode(user_input, metronome_instance)
                continue
            
            # 3. Handle the special case for 0 BPM (easter egg)
            elif user_input == "0":
                print(CURRENT_LANG["0_BPM"])
                continue
            
            # 4. Handle time signature changes
            elif handle_time_signature(user_input, metronome_instance):
                continue
            
            # 5. Handle BPM updates (default if no other command matched)
            metronome_instance = handle_bpm_update(user_input, metronome_instance)
    
    # Handle graceful exit with Ctrl+C
    except KeyboardInterrupt:
        if metronome_instance:
            metronome_instance.stop()
        print("\n" + CURRENT_LANG["GOODBYE_MSG"])

def check_dependencies(check_textual=0):
    """
    Check if required dependencies are installed.
    
    Args:
        check_textual (int, optional): If set to 1, also checks for Textual library. Defaults to 0.
    
    Returns:
        bool: True if all required dependencies are available, False otherwise.
    """
    # Check for pygame first
    try:
        import pygame
        # Test pygame.mixer initialization
        pygame.mixer.init()
        pygame.mixer.quit()
    except (ImportError, pygame.error):
        print(CURRENT_LANG["PYMIXER_ERROR"])
        print(CURRENT_LANG["PYGAME_INSTALL_MSG"])
        return False
    
    # Check for textual if requested
    if check_textual == 1:
        try:
            import textual
        except ImportError:
            print(CURRENT_LANG["TEXTUAL_ERROR"])
            print(CURRENT_LANG["TEXTUAL_INSTALL_MSG"])
            return False
    
    return True
    
# Program entry point
if __name__ == "__main__":
    if check_dependencies(check_textual=0):
        run_metronome()
    else:
        print(CURRENT_LANG["DEPENDENCY_ERROR"])