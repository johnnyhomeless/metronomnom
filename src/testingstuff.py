import os
import sys
import time
import pytest
from unittest.mock import patch, MagicMock, call

# Add the src directory to the path so we can import the modules
sys.path.append('src')

# Import modules to test
from constants import MIN_BPM, MAX_BPM, CURRENT_LANG
from metronome import Metronome, NORMAL_MODE, EIGHTH_MODE, TRIPLET_MODE, SIXTEENTH_MODE
from main import validate_bpm, handle_quit_or_stop, handle_rhythm_mode, handle_time_signature, handle_bpm_update

#===============================================================
# Fixtures
#===============================================================

@pytest.fixture
def mock_pygame():
    """Mock pygame.mixer to avoid actual audio playback during tests"""
    with patch('pygame.mixer') as mock_mixer:
        # Set up mock sound objects
        mock_sound = MagicMock()
        mock_mixer.Sound.return_value = mock_sound
        
        # Set up mock channels
        mock_channel = MagicMock()
        mock_mixer.Channel.return_value = mock_channel
        
        yield mock_mixer

@pytest.fixture
def mock_path():
    """Mock Path.is_file to return True for file checks"""
    with patch('pathlib.Path.is_file', return_value=True):
        yield

@pytest.fixture
def metronome(mock_pygame, mock_path):
    """Create a metronome instance with mocked dependencies"""
    metro = Metronome(120)
    yield metro
    # Clean up
    if metro.is_running:
        metro.stop()

#===============================================================
# Metronome Class Tests
#===============================================================

class TestMetronome:
    """Tests for the Metronome class functionality"""
    
    def test_init(self, metronome):
        """Test Metronome initialization with default values"""
        assert metronome.bpm == 120
        assert metronome.interval == 0.5  # 60/120
        assert metronome.current_beat == 1
        assert metronome.beats_per_measure == 4
        assert metronome.rhythm_mode == NORMAL_MODE
        assert metronome.is_running == False
    
    def test_invalid_bpm(self, mock_pygame, mock_path):
        """Test that initializing with invalid BPM raises ValueError"""
        with pytest.raises(ValueError):
            Metronome(MIN_BPM - 1)
        
        with pytest.raises(ValueError):
            Metronome(MAX_BPM + 1)
    
    def test_update_bpm(self, metronome):
        """Test updating the BPM value"""
        metronome.update_bpm(60)
        assert metronome.bpm == 60
        assert metronome.interval == 1.0  # 60/60
        
        # Test invalid BPM update
        with pytest.raises(ValueError):
            metronome.update_bpm(MIN_BPM - 1)
    
    def test_increment_beat(self, metronome):
        """Test beat incrementation and wrapping at end of measure"""
        metronome.current_beat = 1
        metronome.beats_per_measure = 4
        
        metronome.increment_beat()
        assert metronome.current_beat == 2
        
        metronome.increment_beat()
        assert metronome.current_beat == 3
        
        metronome.increment_beat()
        assert metronome.current_beat == 4
        
        metronome.increment_beat()
        assert metronome.current_beat == 1  # Wrapped around to start of measure
    
    def test_set_rhythm_mode(self, metronome):
        """Test rhythm mode changes"""
        # Initial mode is NORMAL
        assert metronome.rhythm_mode == NORMAL_MODE
        
        # Change to EIGHTH mode
        result = metronome.set_rhythm_mode(EIGHTH_MODE)
        assert metronome.rhythm_mode == EIGHTH_MODE
        assert result == EIGHTH_MODE
        
        # Change to TRIPLET mode
        result = metronome.set_rhythm_mode(TRIPLET_MODE)
        assert metronome.rhythm_mode == TRIPLET_MODE
        assert result == TRIPLET_MODE
        
        # Change to SIXTEENTH mode
        result = metronome.set_rhythm_mode(SIXTEENTH_MODE)
        assert metronome.rhythm_mode == SIXTEENTH_MODE
        assert result == SIXTEENTH_MODE
        
        # Toggle behavior: setting to current mode should switch back to normal
        result = metronome.set_rhythm_mode(SIXTEENTH_MODE)
        assert metronome.rhythm_mode == NORMAL_MODE
        assert result == NORMAL_MODE
        
        # Test invalid mode
        with pytest.raises(ValueError):
            metronome.set_rhythm_mode("invalid_mode")
    
    def test_get_subdivision_interval(self, metronome):
        """Test calculation of subdivision intervals"""
        metronome.bpm = 60
        metronome.interval = 1.0  # 60/60 = 1 second per beat
        
        # Test normal mode (no subdivision)
        metronome.rhythm_mode = NORMAL_MODE
        assert metronome.get_subdivision_interval() == 1.0
        
        # Test eighth notes (half the beat interval)
        metronome.rhythm_mode = EIGHTH_MODE
        assert metronome.get_subdivision_interval() == 0.5
        
        # Test triplets (third of the beat interval)
        metronome.rhythm_mode = TRIPLET_MODE
        assert metronome.get_subdivision_interval() == 1.0/3
        
        # Test sixteenth notes (quarter of the beat interval)
        metronome.rhythm_mode = SIXTEENTH_MODE
        assert metronome.get_subdivision_interval() == 0.25
    
    def test_start_stop(self, metronome, mock_pygame):
        """Test starting and stopping the metronome"""
        # Start metronome
        metronome.start()
        assert metronome.is_running == True
        assert metronome.beat_thread is not None
        
        # Stop metronome
        metronome.stop()
        assert metronome.is_running == False
        
        # Verify pygame.mixer.quit was called
        mock_pygame.quit.assert_called_once()
    
    def test_on_beat_callback(self, mock_pygame, mock_path):
        """Test that the beat callback is called correctly"""
        # Create a mock callback function
        mock_callback = MagicMock()
        
        # Create metronome with mock callback
        metronome = Metronome(60, on_beat=mock_callback)
        
        # Instead of running the whole play_beats method (which is an infinite loop),
        # let's directly test that the callback works when a beat occurs
        
        # Simulate the first beat
        metronome.current_beat = 1
        metronome.on_beat(metronome.current_beat)
        
        # Verify callback was called with correct beat number
        mock_callback.assert_called_once_with(1)
        
        # Simulate another beat
        metronome.increment_beat()
        metronome.on_beat(metronome.current_beat)
        
        # Verify callback was called again with the next beat number
        assert mock_callback.call_count == 2
        mock_callback.assert_called_with(2)

#===============================================================
# Input Validation Tests
#===============================================================

class TestInputValidation:
    """Tests for input validation functions"""
    
    def test_validate_bpm_valid(self):
        """Test validation with valid BPM values"""
        valid_bpms = ["60", "120", f"{MIN_BPM}", f"{MAX_BPM}"]
        
        for bpm_str in valid_bpms:
            is_valid, result = validate_bpm(bpm_str)
            assert is_valid is True
            assert result == int(bpm_str)
    
    def test_validate_bpm_invalid(self):
        """Test validation with invalid BPM values"""
        # Test non-integer input
        is_valid, result = validate_bpm("not_a_number")
        assert is_valid is False
        assert result == CURRENT_LANG["COMMAND_ERROR"]
        
        # Test decimal input
        is_valid, result = validate_bpm("60.5")
        assert is_valid is False
        assert result == CURRENT_LANG["DECIMAL_ERROR_MSG"]
        
        # Test out-of-range values
        is_valid, result = validate_bpm(str(MIN_BPM - 1))
        assert is_valid is False
        assert result == CURRENT_LANG["INVALID_BPM_MSG"]
        
        is_valid, result = validate_bpm(str(MAX_BPM + 1))
        assert is_valid is False
        assert result == CURRENT_LANG["INVALID_BPM_MSG"]

#===============================================================
# Command Handler Tests
#===============================================================

class TestCommandHandlers:
    """Tests for command handler functions"""
    
    def test_handle_quit_or_stop_quit(self, metronome):
        """Test quit command handling"""
        with patch('builtins.print') as mock_print:
            result = handle_quit_or_stop("q", metronome)
            assert result is True  # Should signal to exit
            mock_print.assert_called_with(CURRENT_LANG["GOODBYE_MSG"])
    
    def test_handle_quit_or_stop_stop(self, metronome):
        """Test stop command handling"""
        # First start the metronome
        metronome.start()
        
        with patch('builtins.print') as mock_print:
            result = handle_quit_or_stop("s", metronome)
            assert result is False  # Should not signal to exit
            mock_print.assert_called_with(CURRENT_LANG["METRONOME_STOPPED_MSG"])
            assert metronome.is_running is False
    
    def test_handle_quit_or_stop_not_running(self):
        """Test handling stop when metronome is not running"""
        with patch('builtins.print') as mock_print:
            result = handle_quit_or_stop("s", None)
            assert result is False
            mock_print.assert_called_with(CURRENT_LANG["NOT_RUNNING"])
    
    def test_handle_rhythm_mode(self, metronome):
        """Test rhythm mode command handling"""
        # Start metronome first
        metronome.start()
        
        with patch('builtins.print') as mock_print:
            # Test eighth note mode
            handle_rhythm_mode("e", metronome)
            assert metronome.rhythm_mode == EIGHTH_MODE
            mock_print.assert_called_with(CURRENT_LANG["MODE_EIGHTH"])
            
            # Test triplet mode
            handle_rhythm_mode("t", metronome)
            assert metronome.rhythm_mode == TRIPLET_MODE
            mock_print.assert_called_with(CURRENT_LANG["MODE_TRIPLET"])
            
            # Test sixteenth note mode
            handle_rhythm_mode("x", metronome)
            assert metronome.rhythm_mode == SIXTEENTH_MODE
            mock_print.assert_called_with(CURRENT_LANG["MODE_SIXTEENTH"])
            
            # Test normal mode (toggle)
            handle_rhythm_mode("x", metronome)
            assert metronome.rhythm_mode == NORMAL_MODE
            mock_print.assert_called_with(CURRENT_LANG["MODE_NORMAL"])
    
    def test_handle_rhythm_mode_not_running(self):
        """Test rhythm mode handling when metronome is not running"""
        with patch('builtins.print') as mock_print:
            handle_rhythm_mode("e", None)
            mock_print.assert_called_with(CURRENT_LANG["MODE_CHANGE_STOPPED"])
    
    def test_handle_time_signature(self, metronome):
        """Test time signature handling"""
        with patch('builtins.print') as mock_print:
            # Start metronome
            metronome.start()
            
            # Change time signature
            result = handle_time_signature("3", metronome)
            assert result is True
            assert metronome.beats_per_measure == 3
            assert metronome.current_beat == 1  # Reset to first beat
            mock_print.assert_called_with(CURRENT_LANG["TIME_SIG_CHANGE"].format(3, 4))
    
    def test_handle_time_signature_not_running(self):
        """Test time signature handling when metronome is not running"""
        with patch('builtins.print') as mock_print:
            result = handle_time_signature("3", None)
            assert result is True
            mock_print.assert_called_with(CURRENT_LANG["TIME_SWITCH"].format(3))
    
    def test_handle_time_signature_invalid(self, metronome):
        """Test invalid time signature handling"""
        result = handle_time_signature("0", metronome)
        assert result is False
        
        result = handle_time_signature("10", metronome)
        assert result is False
        
        result = handle_time_signature("not_a_number", metronome)
        assert result is False
    
    def test_handle_bpm_update(self, metronome):
        """Test BPM update handling with existing metronome"""
        with patch('builtins.print') as mock_print:
            # Update BPM on existing metronome
            result = handle_bpm_update("90", metronome)
            assert result is metronome
            assert metronome.bpm == 90
    
    def test_handle_bpm_update_new(self, mock_pygame, mock_path):
        """Test BPM update handling with new metronome"""
        with patch('builtins.print') as mock_print:
            # Create new metronome
            result = handle_bpm_update("90", None)
            assert isinstance(result, Metronome)
            assert result.bpm == 90
            assert result.is_running is True
            
            # Clean up
            result.stop()
    
    def test_handle_bpm_update_invalid(self, metronome):
        """Test BPM update handling with invalid input"""
        with patch('builtins.print') as mock_print:
            # Invalid BPM
            result = handle_bpm_update("not_a_number", metronome)
            assert result is metronome  # Should return unchanged metronome
            mock_print.assert_called_with(CURRENT_LANG["COMMAND_ERROR"])

#===============================================================
# Integration Tests
#===============================================================

class TestIntegration:
    """Integration tests that check multiple components working together"""
    
    def test_metronome_audio_flow(self, metronome, mock_pygame):
        """Test the full audio flow from start to playing beats"""
        # Set up mock channel and sound
        mock_channel = mock_pygame.Channel.return_value
        mock_sound = mock_pygame.Sound.return_value
        
        # Start metronome
        metronome.start()
        
        # Wait briefly to allow beat thread to run
        time.sleep(0.1)
        
        # Stop metronome
        metronome.stop()
        
        # Verify sound loading
        assert mock_pygame.Sound.call_count >= 3  # Main, upbeat, and subdivision sounds
        
        # Verify channel creation
        assert mock_pygame.Channel.call_count >= 1
        
        # Verify some sound was played (we can't easily check specific calls due to threading)
        assert mock_channel.play.call_count >= 1

# Add test cases for UI components if needed
# These would require a different approach due to the nature of Textual UI testing

if __name__ == "__main__":
    print("Running Metronomnom tests...")
    pytest.main(["-v", __file__])