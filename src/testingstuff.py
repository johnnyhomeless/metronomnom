import unittest
from unittest.mock import Mock, patch, call
import time
import pygame
import io
import sys
from contextlib import contextmanager
from metronome import Metronome
from main import validate_bpm, run_metronome
from constants import (
    MIN_BPM, 
    MAX_BPM, 
    CURRENT_LANG, 
    SOUND_FILE,
    QUIT_COMMAND,
    STOP_COMMAND
)

@contextmanager
def capture_output():
    """Capture stdout and stderr for testing"""
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class TestMetronomeUnit(unittest.TestCase):
    """Unit tests for the Metronome class"""
    
    def setUp(self):
        self.valid_bpm = 120
        
    def tearDown(self):
        pygame.mixer.quit()

    @patch('pygame.mixer.init')
    @patch('pygame.mixer.Sound')
    def test_init_valid_bpm(self, mock_sound, mock_init):
        metro = Metronome(self.valid_bpm)
        self.assertEqual(metro.bpm, self.valid_bpm)
        self.assertEqual(metro.interval, 60/self.valid_bpm)
        self.assertFalse(metro.is_running)
        
    def test_init_invalid_bpm(self):
        test_values = [MIN_BPM - 1, MAX_BPM + 1, 0, None, -120]
        for bpm in test_values:
            with self.assertRaises(ValueError):
                Metronome(bpm)
                
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.Sound')
    def test_start_stop(self, mock_sound, mock_init):
        metro = Metronome(self.valid_bpm)
        self.assertFalse(metro.is_running)
        
        metro.start()
        self.assertTrue(metro.is_running)
        self.assertIsNotNone(metro.beat_thread)
        
        metro.stop()
        self.assertFalse(metro.is_running)
        
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.Sound')
    def test_timing_accuracy(self, mock_sound, mock_init):
        metro = Metronome(60)  # 1 beat per second
        start_time = time.perf_counter()
        metro.start()
        time.sleep(3.1)  # Test 3 beats
        metro.stop()
        elapsed = time.perf_counter() - start_time
        self.assertAlmostEqual(elapsed, 3.1, delta=0.1)

class TestInputValidation(unittest.TestCase):
    """Tests for input validation functions"""
    
    def test_validate_bpm_valid(self):
        test_values = [60, 120, MIN_BPM, MAX_BPM]
        for bpm in test_values:
            is_valid, result = validate_bpm(str(bpm))
            self.assertTrue(is_valid)
            self.assertEqual(result, bpm)
            
    def test_validate_bpm_invalid(self):
        test_values = [
            str(MIN_BPM - 1),
            str(MAX_BPM + 1),
            "0",
            "-120",
            "abc",
            "12.5",
            "",
            " "
        ]
        for value in test_values:
            is_valid, message = validate_bpm(value)
            self.assertFalse(is_valid)
            self.assertIsInstance(message, str)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.valid_bpm = 120
    
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.Sound')
    def test_complete_workflow(self, mock_sound, mock_init):
        """Test a complete workflow with start, update, stop, and quit"""
        
        # Simulate user inputs
        inputs = ["120", "140", STOP_COMMAND, "90", QUIT_COMMAND]
        input_mock = Mock(side_effect=inputs)
        
        with patch('builtins.input', input_mock):
            with capture_output() as (out, err):
                run_metronome()
                
        output = out.getvalue()
        
        # Verify expected outputs
        self.assertIn(CURRENT_LANG["METRONOME_STARTED_MSG"], output)
        self.assertIn(CURRENT_LANG["METRONOME_STOPPED_MSG"], output)
        self.assertIn(CURRENT_LANG["GOODBYE_MSG"], output)
        
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.Sound')
    def test_error_handling(self, mock_sound, mock_init):
        """Test system's error handling capabilities"""
        
        # Test with invalid inputs
        inputs = ["abc", "-1", "1000", "0", QUIT_COMMAND]
        input_mock = Mock(side_effect=inputs)
        
        with patch('builtins.input', input_mock):
            with capture_output() as (out, err):
                run_metronome()
                
        output = out.getvalue()
        
        # Verify error messages
        self.assertIn(CURRENT_LANG["COMMAND_ERROR"], output)
        self.assertIn(CURRENT_LANG["INVALID_BPM_MSG"], output)
        self.assertIn(CURRENT_LANG["0_BPM"], output)
        
    @patch('pygame.mixer.init', side_effect=pygame.error)
    def test_audio_device_error(self, mock_init):
        """Test behavior when audio device is not available"""
        
        inputs = [str(self.valid_bpm), QUIT_COMMAND]
        input_mock = Mock(side_effect=inputs)
        
        with patch('builtins.input', input_mock):
            with capture_output() as (out, err):
                run_metronome()
                
        output = out.getvalue()
        self.assertIn(CURRENT_LANG["PYMIXER_ERROR"], output)

if __name__ == '__main__':
    unittest.main(verbosity=2)