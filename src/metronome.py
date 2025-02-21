import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame.mixer
import time
import threading
from pathlib import Path
from constants import (SOUND_FILE, SOUND_FILE_UP, CURRENT_LANG, MIN_BPM, MAX_BPM)

# Rhythm modes
NORMAL_MODE = "normal"
EIGHTH_MODE = "eighth"
TRIPLET_MODE = "triplet"

class Metronome:
    def __init__(self, bpm, on_beat=None, beats_per_measure=4):  # Fixed "None" string to None
        if bpm is None or bpm < MIN_BPM or bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.is_running = False
        self.bpm = bpm
        self.interval = 60 / self.bpm
        self.sound = None
        self.sound_up = None
        self.beat_thread = None
        self.current_beat = 1
        self.beats_per_measure = beats_per_measure
        self.on_beat = on_beat
        self.rhythm_mode = NORMAL_MODE
        
        try:
            pygame.mixer.init()
        except pygame.error:
            print(CURRENT_LANG["PYMIXER_ERROR"])
            return
        
        self.load_sound()
    
    def load_sound(self):
        path = Path(SOUND_FILE)
        path_up = Path(SOUND_FILE_UP)
        if not path.is_file():
           raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_DOWN"])
        if not path_up.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_UP"])
        self.sound = pygame.mixer.Sound(SOUND_FILE)
        self.sound_up = pygame.mixer.Sound(SOUND_FILE_UP)

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

            if not self.sound or not self.sound_up:
                print(CURRENT_LANG["WAV_NOT_LOADED"])
                break  # Exit the loop if sounds are missing
            
            if self.on_beat:
                self.on_beat(self.current_beat)

            # Play the correct sound
            if self.current_beat == 1:
                self.sound.play()
                print(CURRENT_LANG["FIRST_BEAT"].format(self.current_beat), end='\r')
            else:
                self.sound_up.play()
                print(CURRENT_LANG["OTHER_BEAT"].format(self.current_beat), end='\r')

            self.increment_beat()

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            wait_time = max(0, int((self.interval - elapsed_time) * 1000))  # Convert to milliseconds

            # Use pygame.time.wait() instead of time.sleep()
            pygame.time.wait(wait_time)

    
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