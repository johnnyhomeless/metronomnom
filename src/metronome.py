import os
import pygame.mixer
import time
import threading
from pathlib import Path
from constants import (SOUND_FILE, SOUND_FILE_UP, SOUND_FILE_SUBDIVISION, CURRENT_LANG, MIN_BPM, MAX_BPM)

# Hide Pygame's startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Rhythm modes
NORMAL_MODE = "normal"
EIGHTH_MODE = "eighth"
TRIPLET_MODE = "triplet"

class Metronome:
    def __init__(self, bpm, on_beat=None, beats_per_measure=4):
        if bpm is None or bpm < MIN_BPM or bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.is_running = False
        self.bpm = bpm
        self.interval = 60 / self.bpm
        self.sound = None
        self.sound_up = None
        self.sound_subdivision = None
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
        path_subdivision = Path(SOUND_FILE_SUBDIVISION)

        if not path.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_DOWN"])
        if not path_up.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_UP"])
        if not path_subdivision.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_SUBDIVISION"])
        
        self.sound = pygame.mixer.Sound(SOUND_FILE)
        self.sound_up = pygame.mixer.Sound(SOUND_FILE_UP)
        self.sound_subdivision = pygame.mixer.Sound(SOUND_FILE_SUBDIVISION)

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
        channel = pygame.mixer.Channel(0)         # Regular beats
        channel_up = pygame.mixer.Channel(1)      # First beat accent
        channel_subdivision = pygame.mixer.Channel(2)  # Subdivisions
        
        while self.is_running:
            start_time = time.time()
            subdivision_interval = self.get_subdivision_interval()

            if not all([self.sound, self.sound_up, self.sound_subdivision]):
                print(CURRENT_LANG["WAV_NOT_LOADED"])
                break

            if self.on_beat:
                self.on_beat(self.current_beat)

            # Play main beat
            if self.current_beat == 1:
                channel_up.play(self.sound)
                print(CURRENT_LANG["FIRST_BEAT"].format(self.current_beat), end='\r')
            else:
                channel.play(self.sound_up)
                print(CURRENT_LANG["OTHER_BEAT"].format(self.current_beat), end='\r')

            # Play subdivisions if not in normal mode
            if self.rhythm_mode != NORMAL_MODE:
                # Wait a subdivision interval
                pygame.time.wait(int(subdivision_interval * 1000))
                
                # Play subdivision sounds
                subdivisions = 2 if self.rhythm_mode == EIGHTH_MODE else 3
                for _ in range(subdivisions - 1):  # -1 because we already played the main beat
                    channel_subdivision.play(self.sound_subdivision)
                    pygame.time.wait(int(subdivision_interval * 1000))

            self.increment_beat()

            # Calculate remaining time in the beat after subdivisions
            elapsed_time = time.time() - start_time
            wait_time = max(0, int((self.interval - elapsed_time) * 1000))
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

    def set_rhythm_mode(self, mode):
        """Toggle between rhythm modes."""
        valid_modes = {NORMAL_MODE, EIGHTH_MODE, TRIPLET_MODE}
        
        if mode not in valid_modes:
            raise ValueError(CURRENT_LANG["INVALID_MODE"])
        
        # If selecting current mode, switch to normal
        if mode == self.rhythm_mode:
            self.rhythm_mode = NORMAL_MODE
        else:
            self.rhythm_mode = mode
        
        return self.rhythm_mode

    def get_subdivision_interval(self):
        """Calculate interval time for subdivisions based on rhythm mode."""
        base_interval = self.interval  # Current beat interval (60/bpm)
        
        if self.rhythm_mode == EIGHTH_MODE:
            return base_interval / 2  # Two subdivisions per beat
        elif self.rhythm_mode == TRIPLET_MODE:
            return base_interval / 3  # Three subdivisions per beat
        
        return base_interval  # Normal mode, no subdivision