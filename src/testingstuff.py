import unittest
from unittest.mock import patch, MagicMock
from metronome import Metronome
from constants import MIN_BPM, MAX_BPM, CURRENT_LANG
from main import validate_bpm

class TestMetronome(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.valid_bpm = 120
        self.metronome = None
    
    def tearDown(self):
        """Clean up after each test"""
        if self.metronome and self.metronome.is_running:
            self.metronome.stop()

    # BPM Validation Tests
    def test_valid_bpm(self):
        """Test valid BPM inputs"""
        test_cases = [
            ("120", True, 120),  # Normal case
            (str(MIN_BPM), True, MIN_BPM),  # Minimum value
            (str(MAX_BPM), True, MAX_BPM),  # Maximum value
            ("60", True, 60),    # Common tempo
        ]
        for input_bpm, expected_valid, expected_value in test_cases:
            is_valid, result = validate_bpm(input_bpm)
            self.assertEqual(is_valid, expected_valid)
            if expected_valid:
                self.assertEqual(result, expected_value)

    def test_invalid_bpm(self):
        """Test invalid BPM inputs"""
        test_cases = [
            ("0", False),            # Zero BPM
            ("-1", False),           # Negative BPM
            ("401", False),          # Above maximum
            ("9", False),            # Below minimum
            ("abc", False),          # Non-numeric
            ("120.5", False),        # Decimal number
            ("", False),             # Empty string
            (" ", False),            # Space
        ]
        for input_bpm, expected_valid in test_cases:
            is_valid, _ = validate_bpm(input_bpm)
            self.assertEqual(is_valid, expected_valid)

    # Metronome Class Tests
    def test_metronome_initialization(self):
        """Test Metronome class initialization"""
        self.metronome = Metronome(self.valid_bpm)
        self.assertEqual(self.metronome.bpm, self.valid_bpm)
        self.assertEqual(self.metronome.interval, 60/self.valid_bpm)
        self.assertFalse(self.metronome.is_running)

    def test_invalid_metronome_initialization(self):
        """Test invalid Metronome initialization"""
        invalid_bpms = [None, MIN_BPM-1, MAX_BPM+1, 0, -1]
        for bpm in invalid_bpms:
            with self.assertRaises(ValueError):
                Metronome(bpm)

    @patch('pygame.mixer.Sound')
    def test_sound_loading(self, mock_sound):
        """Test sound loading functionality"""
        self.metronome = Metronome(self.valid_bpm)
        self.assertIsNotNone(self.metronome.sound)

    def test_bpm_update(self):
        """Test BPM update functionality"""
        self.metronome = Metronome(self.valid_bpm)
        new_bpm = 100
        self.metronome.update_bpm(new_bpm)
        self.assertEqual(self.metronome.bpm, new_bpm)
        self.assertEqual(self.metronome.interval, 60/new_bpm)

    def test_invalid_bpm_update(self):
        """Test invalid BPM updates"""
        self.metronome = Metronome(self.valid_bpm)
        invalid_bpms = [None, MIN_BPM-1, MAX_BPM+1, 0, -1]
        for bpm in invalid_bpms:
            with self.assertRaises(ValueError):
                self.metronome.update_bpm(bpm)

    # Thread Control Tests
    def test_start_stop(self):
        """Test start and stop functionality"""
        self.metronome = Metronome(self.valid_bpm)
        self.metronome.start()
        self.assertTrue(self.metronome.is_running)
        self.assertIsNotNone(self.metronome.beat_thread)
        
        self.metronome.stop()
        self.assertFalse(self.metronome.is_running)

    # Command Tests
    @patch('builtins.input', side_effect=['q'])
    def test_quit_command(self, mock_input):
        """Test quit command"""
        from main import run_metronome
        run_metronome()
        mock_input.assert_called_once()

    @patch('builtins.input', side_effect=['120', 's', 'q'])
    def test_stop_command(self, mock_input):
        """Test stop command"""
        from main import run_metronome
        run_metronome()
        self.assertEqual(mock_input.call_count, 3)

if __name__ == '__main__':
    unittest.main()