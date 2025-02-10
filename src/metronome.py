import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame.mixer
import time
import threading
from pathlib import Path
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
    
    def load_sound(self):
        path = Path(SOUND_FILE)
        if path.is_file():
            self.sound = pygame.mixer.Sound(SOUND_FILE)
        else:
            print(CURRENT_LANG["NOWAVE_FILE"])
            self.sound = None
    
    def start(self):
        if not self.is_running and self.sound:
            self.is_running = True
            self.beat_thread = threading.Thread(target=self.play_beats)
            self.beat_thread.start()
    
    def stop(self):
        if self.is_running:
            self.is_running = False  # Tell thread to stop
            if self.beat_thread and self.beat_thread.is_alive():
                self.beat_thread.join(timeout=0.01)  # Avoid blocking too long
            pygame.mixer.quit()

        
    def play_beats(self):
        next_beat_time = time.perf_counter()
        
        while self.is_running:
            if self.sound:
                self.sound.play()
            
            next_beat_time += self.interval  # Schedule next beat precisely
            
            while self.is_running and time.perf_counter() < next_beat_time:
                time.sleep(0.001)  # Small sleep to reduce CPU usage

    
    def play_sound(self):
        if self.sound:
            self.sound.play()
    
    def update_bpm(self, new_bpm):
        if new_bpm is None or new_bpm < MIN_BPM or new_bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.bpm = new_bpm
        self.interval = 60 / new_bpm
