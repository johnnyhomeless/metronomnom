import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame.mixer
from pathlib import Path
import time
import threading
from constants import (SOUND_FILE, CURRENT_LANG, MIN_BPM, MAX_BPM)


class Metronome:
    def __init__(self, bpm):
        if bpm is None or bpm < MIN_BPM or bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.is_running = False
        self.bpm = bpm
        self.interval = 60 / self.bpm
        self.sound = None
        self.beat_thread = None
        
        try:
            pygame.mixer.init()
        except pygame.error:
            print(CURRENT_LANG["PYMIXER_ERROR"])
            return
        
        self.load_sound()
    
    def start(self):
        if not self.is_running and self.sound:
            self.is_running = True
            print(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} {self.bpm} BPM")
            self.beat_thread = threading.Thread(target=self.play_beats)
            self.beat_thread.start()
    
    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.sound:
                self.sound.stop()
            if self.beat_thread:
                self.beat_thread.join()
            pygame.mixer.quit()
            print(CURRENT_LANG["METRONOME_STOPPED_MSG"])
    
    def play_beats(self):
        while self.is_running:
            if self.sound:
                self.sound.play()
            time.sleep(self.interval)
    
    def load_sound(self):
        path = Path(SOUND_FILE)
        if path.is_file():
            self.sound = pygame.mixer.Sound(SOUND_FILE)
        else:
            print(CURRENT_LANG["NOWAVE_FILE"])
            self.sound = None
    
    def play_sound(self):
        if self.sound:
            self.sound.play()
