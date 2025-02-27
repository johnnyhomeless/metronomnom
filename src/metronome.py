import os
import time
import threading
import pygame.mixer
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

#-------------------------------------------------------
# Rhythm mode constants
#-------------------------------------------------------
NORMAL_MODE = "normal"      # Regular beats only
EIGHTH_MODE = "eighth"      # Two subdivisions per beat
TRIPLET_MODE = "triplet"    # Three subdivisions per beat
SIXTEENTH_MODE = "sixteenth"  # Four subdivisions per beat


class Metronome:
    """
    A metronome class that provides timing, beat counting, and audio feedback
    with support for different rhythm modes and time signatures.
    
    Features:
    - Multiple rhythm modes (normal, eighth notes, triplets, sixteenth notes)
    - Customizable tempo (BPM)
    - Variable time signatures
    - Accent on first beat of measure
    - Beat callback for UI integration
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
        # Input validation
        if bpm is None or bpm < MIN_BPM or bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        #----------------------------
        # State variables
        #----------------------------
        self.is_running = False
        self.bpm = bpm
        self.interval = 60 / self.bpm  # Beat interval in seconds
        self.current_beat = 1          # Start on first beat
        self.beats_per_measure = beats_per_measure
        self.rhythm_mode = NORMAL_MODE
        
        #----------------------------
        # Audio variables
        #----------------------------
        self.sound = None              # Main beat sound
        self.sound_up = None           # Upbeat sound
        self.sound_subdivision = None  # Subdivision sound
        
        #----------------------------
        # Thread control
        #----------------------------
        self.beat_thread = None
        
        # Callback for UI updates or other notifications
        self.on_beat = on_beat
        
        # Initialize audio system
        try:
            pygame.mixer.init()
        except pygame.error:
            print(CURRENT_LANG["PYMIXER_ERROR"])
            return
        
        # Load audio files
        self.load_sound()
    
    #=======================================================
    # Sound Management Methods
    #=======================================================
    
    def load_sound(self):
        """
        Load sound files for metronome beats and subdivisions.
        
        Raises:
            FileNotFoundError: If any required sound file is missing
        """
        # Create Path objects for each sound file
        path = Path(SOUND_FILE)
        path_up = Path(SOUND_FILE_UP)
        path_subdivision = Path(SOUND_FILE_SUBDIVISION)

        # Verify all sound files exist before trying to load them
        if not path.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_DOWN"])
        if not path_up.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_UP"])
        if not path_subdivision.is_file():
            raise FileNotFoundError(CURRENT_LANG["NOWAVE_FILE_SUBDIVISION"])
        
        # Load sounds into pygame mixer
        self.sound = pygame.mixer.Sound(SOUND_FILE)
        self.sound_up = pygame.mixer.Sound(SOUND_FILE_UP)
        self.sound_subdivision = pygame.mixer.Sound(SOUND_FILE_SUBDIVISION)

    def _play_main_beat(self, channel, channel_up):
        """
        Play the main beat sound with appropriate accent.
        
        Args:
            channel (pygame.mixer.Channel): Channel for regular beats
            channel_up (pygame.mixer.Channel): Channel for accented beats
        """
        # First beat gets accent (different sound and channel)
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
        
        # Wait for first subdivision after main beat
        pygame.time.wait(int(subdivision_interval * 1000))
        
        # Determine number of subdivisions based on rhythm mode
        if self.rhythm_mode == EIGHTH_MODE:
            subdivisions = 2      # Two sounds per beat
        elif self.rhythm_mode == TRIPLET_MODE:
            subdivisions = 3      # Three sounds per beat
        elif self.rhythm_mode == SIXTEENTH_MODE:
            subdivisions = 4      # Four sounds per beat
        else:
            subdivisions = 1      # Fallback, should never happen
            
        # Play remaining subdivision sounds after the main beat
        # (-1 because we already played the main beat)
        for _ in range(subdivisions - 1):
            channel_subdivision.play(self.sound_subdivision)
            pygame.time.wait(int(subdivision_interval * 1000))
    
    #=======================================================
    # Core Metronome Control Methods
    #=======================================================
    
    def start(self):
        """
        Start the metronome if it's not already running and sounds are loaded.
        Creates and launches a thread for the beat playback loop.
        """
        if not self.is_running and self.sound:
            self.is_running = True
            self.beat_thread = threading.Thread(target=self.play_beats)
            self.beat_thread.start()
    
    def stop(self):
        """
        Stop the metronome if it's running and clean up resources.
        Waits for the beat thread to finish and closes the audio system.
        """
        if self.is_running:
            self.is_running = False  # Signal thread to stop
            if self.sound:
                self.sound.stop()    # Stop any playing sounds
            if self.beat_thread:
                self.beat_thread.join()  # Wait for thread to end
            pygame.mixer.quit()      # Clean up audio system
    
    def update_bpm(self, new_bpm):
        """
        Update the metronome's BPM (beats per minute).
        
        Args:
            new_bpm (int): New BPM value
            
        Raises:
            ValueError: If BPM is outside valid range
        """
        # Validate new BPM value
        if new_bpm is None or new_bpm < MIN_BPM or new_bpm > MAX_BPM:
            raise ValueError(CURRENT_LANG["INVALID_BPM_INIT"])
        
        self.bpm = new_bpm
        self.interval = 60 / new_bpm  # Recalculate interval in seconds

    def increment_beat(self):
        """
        Increment the current beat counter, resetting at the end of a measure.
        """
        if self.current_beat < self.beats_per_measure:
            self.current_beat += 1   # Move to next beat in measure
        else:
            self.current_beat = 1    # Reset to first beat of new measure

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
        # Define valid rhythm modes
        valid_modes = {NORMAL_MODE, EIGHTH_MODE, TRIPLET_MODE, SIXTEENTH_MODE}
        
        # Validate the requested mode
        if mode not in valid_modes:
            raise ValueError(CURRENT_LANG["INVALID_MODE"])
        
        # Toggle behavior: if selecting current mode, switch to normal
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
        
        # Return smaller intervals for subdivision modes
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
        This runs in a separate thread to maintain timing accuracy.
        """
        # Set up audio channels for different sound types
        channel = pygame.mixer.Channel(0)             # Regular beats
        channel_up = pygame.mixer.Channel(1)          # First beat accent
        channel_subdivision = pygame.mixer.Channel(2) # Subdivisions
        
        # Main beat playback loop
        while self.is_running:
            start_time = time.time()  # Track when we start this beat cycle
            subdivision_interval = self.get_subdivision_interval()

            # Safety check - verify sounds are loaded
            if not all([self.sound, self.sound_up, self.sound_subdivision]):
                print(CURRENT_LANG["WAV_NOT_LOADED"])
                break

            # Notify UI or other listeners about the beat
            if self.on_beat:
                self.on_beat(self.current_beat)

            # Play the main beat sound
            self._play_main_beat(channel, channel_up)

            # Play any subdivision beats if needed
            self._play_subdivisions(channel_subdivision, subdivision_interval)

            # Move to next beat in the measure
            self.increment_beat()

            # Calculate how long to wait until next beat
            # This accounts for processing time to keep accurate tempo
            elapsed_time = time.time() - start_time
            wait_time = max(0, int((self.interval - elapsed_time) * 1000))
            pygame.time.wait(wait_time)