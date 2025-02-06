import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame.mixer
import time
import threading
import os
from constants import (PYMIXER_ERROR, 
                       SOUND_FILE,
                       CURRENT_LANG)


class Metronome:
    def __init__(self, bpm=None):
        try:
            pygame.mixer.init()
        except pygame.error:
            print(CURRENT_LANG["PYMIXER_ERROR"])
            return
