import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame.mixer
import time
import threading
from pathlib import Path
from constants import (SOUND_FILE, SOUND_FILE_LO, CURRENT_LANG, MIN_BPM, MAX_BPM)

class Metronome:
    def __init__(self, bpm):
        if bpm is None or bpm < MIN_BPM or bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.is_running = False
        self.bpm = bpm
        self.interval = 60 / self.bpm
        self.sound = None
        self.beat_thread = None
        self.eight_notes_on = False
        self.sound_lo = None        
        
        try:
            pygame.mixer.init()
        except pygame.error:
            print(CURRENT_LANG["PYMIXER_ERROR"])
            return
        
        self.load_sound()
    
    def load_sound(self):
        main_path = Path(SOUND_FILE)
        lo_path = Path(SOUND_FILE_LO)
        
        if main_path.is_file():
            self.sound = pygame.mixer.Sound(SOUND_FILE)
        else:
            print(CURRENT_LANG["NOWAVE_FILE"])
            self.sound = None
            
        if lo_path.is_file():
            self.sound_lo = pygame.mixer.Sound(SOUND_FILE_LO)
        else:
            print(CURRENT_LANG["NOWAVE_FILE"])
            self.sound_lo = None
    
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
        is_main_beat = True
        
        while self.is_running:
            current_time = time.perf_counter()
            
            if current_time >= next_beat_time:
                if is_main_beat:
                    if self.sound:
                        self.sound.play()
                elif self.eight_notes_on and self.sound_lo:
                    self.sound_lo.play()
                
                if self.eight_notes_on:
                    next_beat_time += self.interval / 2
                    is_main_beat = not is_main_beat
                else:
                    next_beat_time += self.interval
                    is_main_beat = True
                    
            sleep_time = max(0, next_beat_time - time.perf_counter())
            time.sleep(sleep_time)

    
    def play_sound(self):
        if self.sound:
            self.sound.play()
    
    def update_bpm(self, new_bpm):
        if new_bpm is None or new_bpm < MIN_BPM or new_bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.bpm = new_bpm
        self.interval = 60 / new_bpm
