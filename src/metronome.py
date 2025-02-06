import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame.mixer
from pathlib import Path
import time
import threading
from constants import (SOUND_FILE,
                       CURRENT_LANG,
                       )


class Metronome:
    def __init__(self, bpm=None):
        try:
            pygame.mixer.init()
        except pygame.error:
            print(CURRENT_LANG["PYMIXER_ERROR"])
            return


def checkwavefile():
    path = Path(SOUND_FILE)

    if path.is_file():
        return True
    print(CURRENT_LANG["NOWAVE_FILE"])
    return False
        
