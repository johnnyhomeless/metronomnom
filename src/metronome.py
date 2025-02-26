import os
import pygame.mixer
import time
import threading
from pathlib import Path
from constants import (
    SOUND_FILE,
    SOUND_FILE_UP,
    SOUND_FILE_SUBDIVISION,
    CURRENT_LANG,
    MIN_BPM,
    MAX_BPM
)

# Hide Pygame's startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Rhythm modes
NORMAL_MODE = "normal"
EIGHTH_MODE = "eighth"
TRIPLET_MODE = "triplet"
SIXTEENTH_MODE = "sixteenth"


class Metronome:
    """
    A metronome class that provides timing, beat counting, and audio feedback
    with support for different rhythm modes and time signatures.
    """
    
    def __init__(self, bpm, on_beat=None, beats_per_measure=4):
        """
        Initialize a new metronome instance.
        
        Args:
            bpm (int): Beats per minute
            on_beat (function, optional): Callback function when a beat occurs
            beats_per_measure (int, optional): Number of beats per measure, defaults to 4
            
        Raises:
            ValueError: If BPM is outside valid range
        """
        if bpm is None or bpm < MIN_BPM or bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        # State variables
        self.is_running = False
        self.bpm = bpm
        self.interval = 60 / self.bpm
        self.current_beat = 1
        self.beats_per_measure = beats_per_measure
        self.rhythm_mode = NORMAL_MODE
        
        # Audio variables
        self.sound = None
        self.sound_up = None
        self.sound_subdivision = None
        
        # Thread control
        self.beat_thread = None
        
        # Callback
        self.on_beat = on_beat
        
        # Initialize audio
        try:
            pygame.mixer.init()
        except pygame.error:
            print(CURRENT_LANG["PYMIXER_ERROR"])
            return
        
        self.load_sound()
    
    def load_sound(self):
        """
        Load sound files for metronome beats and subdivisions.
        
        Raises:
            FileNotFoundError: If any required sound file is missing
        """
        path = Path(SOUND_FILE)
        path_up = Path(SOUND_FILE_UP)
        path_subdivision = Path(SOUND_FILE_SUBDIVISION)

        # Verify all sound files exist
        if not path.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_DOWN"])
        if not path_up.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_UP"])
        if not path_subdivision.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_SUBDIVISION"])
        
        # Load sounds
        self.sound = pygame.mixer.Sound(SOUND_FILE)
        self.sound_up = pygame.mixer.Sound(SOUND_FILE_UP)
        self.sound_subdivision = pygame.mixer.Sound(SOUND_FILE_SUBDIVISION)

    def start(self):
        """
        Start the metronome if it's not already running and sounds are loaded.
        """
        if not self.is_running and self.sound:
            self.is_running = True
            self.beat_thread = threading.Thread(target=self.play_beats)
            self.beat_thread.start()
    
    def stop(self):
        """
        Stop the metronome if it's running and clean up resources.
        """
        if self.is_running:
            self.is_running = False
            if self.sound:
                self.sound.stop()
            if self.beat_thread:
                self.beat_thread.join()
            pygame.mixer.quit()
    
    def update_bpm(self, new_bpm):
        """
        Update the metronome's BPM (beats per minute).
        
        Args:
            new_bpm (int): New BPM value
            
        Raises:
            ValueError: If BPM is outside valid range
        """
        if new_bpm is None or new_bpm < MIN_BPM or new_bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.bpm = new_bpm
        self.interval = 60 / new_bpm  # Update interval for new BPM

    def increment_beat(self):
        """
        Increment the current beat counter, resetting at the end of a measure.
        """
        if self.current_beat < self.beats_per_measure:
            self.current_beat += 1
        else:
            self.current_beat = 1

    def set_rhythm_mode(self, mode):
        """
        Set the rhythm mode (normal, eighth, triplet, or sixteenth).
        
        Args:
            mode (str): The rhythm mode to set
            
        Returns:
            str: The current rhythm mode after setting
            
        Raises:
            ValueError: If an invalid mode is provided
        """
        valid_modes = {NORMAL_MODE, EIGHTH_MODE, TRIPLET_MODE, SIXTEENTH_MODE}
        
        if mode not in valid_modes:
            raise ValueError(CURRENT_LANG["INVALID_MODE"])
        
        # If selecting current mode, switch to normal
        if mode == self.rhythm_mode:
            self.rhythm_mode = NORMAL_MODE
        else:
            self.rhythm_mode = mode
        
        return self.rhythm_mode

    def get_subdivision_interval(self):
        """
        Calculate interval time for subdivisions based on rhythm mode.
        
        Returns:
            float: Time interval in seconds for the current subdivision
        """
        base_interval = self.interval  # Current beat interval (60/bpm)
        
        if self.rhythm_mode == EIGHTH_MODE:
            return base_interval / 2  # Two subdivisions per beat
        elif self.rhythm_mode == TRIPLET_MODE:
            return base_interval / 3  # Three subdivisions per beat
        elif self.rhythm_mode == SIXTEENTH_MODE:
            return base_interval / 4  # Four subdivisions per beat
        
        return base_interval  # Normal mode, no subdivision
    
    def play_beats(self):
        """
        Main loop for playing metronome beats and subdivisions.
        """
        # Set up audio channels
        channel = pygame.mixer.Channel(0)         # Regular beats
        channel_up = pygame.mixer.Channel(1)      # First beat accent
        channel_subdivision = pygame.mixer.Channel(2)  # Subdivisions
        
        while self.is_running:
            start_time = time.time()
            subdivision_interval = self.get_subdivision_interval()

            # Verify sounds are loaded
            if not all([self.sound, self.sound_up, self.sound_subdivision]):
                print(CURRENT_LANG["WAV_NOT_LOADED"])
                break

            # Call the beat callback if provided
            if self.on_beat:
                self.on_beat(self.current_beat)

            # Play main beat with appropriate sound for downbeat/upbeat
            self._play_main_beat(channel, channel_up)

            # Play subdivisions if needed
            self._play_subdivisions(channel_subdivision, subdivision_interval)

            # Move to next beat
            self.increment_beat()

            # Calculate remaining time and wait
            elapsed_time = time.time() - start_time
            wait_time = max(0, int((self.interval - elapsed_time) * 1000))
            pygame.time.wait(wait_time)
    
    def _play_main_beat(self, channel, channel_up):
        """
        Play the main beat sound with appropriate accent.
        
        Args:
            channel (pygame.mixer.Channel): Channel for regular beats
            channel_up (pygame.mixer.Channel): Channel for accented beats
        """
        if self.current_beat == 1:
            channel_up.play(self.sound)
        else:
            channel.play(self.sound_up)
    
    def _play_subdivisions(self, channel_subdivision, subdivision_interval):
        """
        Play subdivision sounds based on current rhythm mode.
        
        Args:
            channel_subdivision (pygame.mixer.Channel): Channel for subdivision sounds
            subdivision_interval (float): Time interval for subdivisions
        """
        # Skip if in normal mode (no subdivisions)
        if self.rhythm_mode == NORMAL_MODE:
            return
        
        # Wait a subdivision interval
        pygame.time.wait(int(subdivision_interval * 1000))
        
        # Determine number of subdivisions based on rhythm mode
        if self.rhythm_mode == EIGHTH_MODE:
            subdivisions = 2
        elif self.rhythm_mode == TRIPLET_MODE:
            subdivisions = 3
        elif self.rhythm_mode == SIXTEENTH_MODE:
            subdivisions = 4
        else:
            subdivisions = 1  # Fallback, should never happen
            
        # Play subdivision sounds
        for _ in range(subdivisions - 1):  # -1 because we already played the main beat
            channel_subdivision.play(self.sound_subdivision)
            pygame.time.wait(int(subdivision_interval * 1000))