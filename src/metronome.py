import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame.mixer
import time
import threading
from pathlib import Path
from constants import (SOUND_FILE, CURRENT_LANG, MIN_BPM, MAX_BPM)

class Metronome:
    def __init__(self, bpm, on_beat=None, beats_per_measure=4):  # Fixed "None" string to None
        if bpm is None or bpm < MIN_BPM or bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.is_running = False
        self.bpm = bpm
        self.interval = 60 / self.bpm
        self.sound = None
        self.beat_thread = None
        self.current_beat = 1
        self.beats_per_measure = beats_per_measure
        self.on_beat = on_beat
        
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
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE"])
    
    def start(self):
        if not self.is_running and self.sound:
            self.is_running = True
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
    
    def play_beats(self):
        while self.is_running:
            start_time = time.time()
            
            if self.sound:
                self.sound.play()
                # Call the callback if it exists
                if self.on_beat:
                    self.on_beat(self.current_beat)
                
                if self.current_beat == 1:
                    print(CURRENT_LANG["FIRST_BEAT"].format(self.current_beat), end='\r')
                else:
                    print(CURRENT_LANG["OTHER_BEAT"].format(self.current_beat), end='\r')
                
                self.increment_beat()
                
                # Calculate and apply sleep time
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.interval - elapsed_time)
                time.sleep(sleep_time)
    
    def update_bpm(self, new_bpm):
        if new_bpm is None or new_bpm < MIN_BPM or new_bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.bpm = new_bpm
        self.interval = 60 / new_bpm  # Update interval for new BPM

    def increment_beat(self):
        if self.current_beat < self.beats_per_measure:
            self.current_beat += 1
        else:
            self.current_beat = 1