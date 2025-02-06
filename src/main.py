from constants import (MIN_BPM,
                      MAX_BPM,
                      SOUND_FILE,
                      QUIT_COMMAND,
                      STOP_COMMAND,
                      CURRENT_LANG)

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
    while True:
        try:
            user_input = input(CURRENT_LANG["PROMPT_BPM"]).strip().lower()

            if user_input == QUIT_COMMAND:
                print(CURRENT_LANG["GOODBYE_MSG"])
                break
            elif user_input == STOP_COMMAND:
                print(CURRENT_LANG["METRONOME_STOPPED_MSG"])
            elif user_input == "0":
                print(CURRENT_LANG["0_BPM"])
            else:
                is_valid, result = validate_bpm(user_input)
                if is_valid:
                    print(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} {result} BPM")
                else:
                    print(result)

        except KeyboardInterrupt:
            print("\n" + CURRENT_LANG["GOODBYE_MSG"])
            break

if __name__ == "__main__":
    run_metronome()
