import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame.mixer
from pathlib import Path
import time
import threading
from constants import (SOUND_FILE,
                       CURRENT_LANG,
                       MIN_BPM,
                       MAX_BPM                       
                       )


class Metronome:
    def __init__(self, bpm):
        self.is_running = False
        self.bpm = bpm
        
        if self.bpm is None or self.bpm < MIN_BPM or self.bpm > MAX_BPM:
            raise Exception(CURRENT_LANG["INVALID_BPM_INIT"])
            
        try:
            pygame.mixer.init()
        except pygame.error:
            print(CURRENT_LANG["PYMIXER_ERROR"])
            return
            
        self.interval = self.calculate_interval()
        self.load_sound()

    def calculate_interval(self):
        return 60 / self.bpm
    
    def play_beats(self):
        while self.is_running:
            if self.sound:
                self.sound.play()
                time.sleep(self.interval)

    def load_sound(self):
        if check_wav_file():
            self.sound = pygame.mixer.Sound(SOUND_FILE)
            return True
        else:
            print(CURRENT_LANG["NOWAVE_FILE"])
            return False
    
    def play_sound(self):
        if self.sound:
            self.sound.play()
    

def check_wav_file():
    path = Path(SOUND_FILE)
    return path.is_file()  
