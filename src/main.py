from constants import (
    MIN_BPM,
    MAX_BPM,
    QUIT_COMMAND,
    STOP_COMMAND,
    CURRENT_LANG
)

from metronome import Metronome

def validate_bpm(user_input):
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

def run_metronome():
    metronome_instance = None

    try:
        while True:
            user_input = input(CURRENT_LANG["PROMPT_BPM"]).strip().lower()
            
            if user_input in {QUIT_COMMAND, STOP_COMMAND}:
                if metronome_instance:
                    metronome_instance.stop()
                
                if user_input == QUIT_COMMAND:
                    print(CURRENT_LANG["GOODBYE_MSG"])
                    break
                
                print(CURRENT_LANG["METRONOME_STOPPED_MSG"])
                continue
            
            elif user_input == "0":
                print(CURRENT_LANG["0_BPM"])
            
            is_valid, result = validate_bpm(user_input)
            
            if is_valid:
                if metronome_instance is None:
                    metronome_instance = Metronome(result)
                    metronome_instance.start()
                    print(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} {result} BPM")
                else:
                    metronome_instance.update_bpm(result)
            else:
                print(result)
    
    except KeyboardInterrupt:
        if metronome_instance:
            metronome_instance.stop()
        
        print("\n" + CURRENT_LANG["GOODBYE_MSG"])
        
if __name__ == "__main__":
    run_metronome()
