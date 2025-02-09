import unittest
from unittest.mock import patch, MagicMock
from metronome import Metronome
from constants import CURRENT_LANG, SOUND_FILE, MIN_BPM, MAX_BPM

class TestMetronome(unittest.TestCase):
    
    @patch("metronome.pygame.mixer")
    def test_initialization_valid_bpm(self, mock_mixer):
        mock_mixer.init.return_value = None
        metronome = Metronome(120)
        self.assertEqual(metronome.bpm, 120)
        self.assertFalse(metronome.is_running)
        self.assertIsNotNone(metronome.interval)
    
    def test_initialization_invalid_bpm(self):
        with self.assertRaises(ValueError) as context:
            Metronome(MIN_BPM - 1)
        self.assertEqual(str(context.exception), CURRENT_LANG["INVALID_BPM_INIT"])
        
        with self.assertRaises(ValueError) as context:
            Metronome(MAX_BPM + 1)
        self.assertEqual(str(context.exception), CURRENT_LANG["INVALID_BPM_INIT"])
    
    @patch("metronome.pygame.mixer")
    def test_load_sound_file_not_found(self, mock_mixer):
        mock_mixer.init.return_value = None
        with patch("metronome.Path.is_file", return_value=False), patch("builtins.print") as mock_print:
            metronome = Metronome(120)
            self.assertIsNone(metronome.sound)
            mock_print.assert_called_with(CURRENT_LANG["NOWAVE_FILE"])
    
    @patch("metronome.pygame.mixer")
    def test_load_sound_file_found(self, mock_mixer):
        mock_mixer.init.return_value = None
        mock_mixer.Sound.return_value = MagicMock()
        with patch("metronome.Path.is_file", return_value=True):
            metronome = Metronome(120)
            self.assertIsNotNone(metronome.sound)
    
    @patch("metronome.pygame.mixer")
    def test_start_metronome(self, mock_mixer):
        mock_mixer.init.return_value = None
        mock_mixer.Sound.return_value = MagicMock()
        with patch("metronome.Path.is_file", return_value=True):
            metronome = Metronome(120)
            with patch("builtins.print") as mock_print:
                metronome.start()
                self.assertTrue(metronome.is_running)
                mock_print.assert_any_call(f"{CURRENT_LANG['METRONOME_STARTED_MSG']} 120 BPM")
            metronome.stop()
    
    @patch("metronome.pygame.mixer")
    def test_stop_metronome(self, mock_mixer):
        mock_mixer.init.return_value = None
        mock_mixer.Sound.return_value = MagicMock()
        with patch("metronome.Path.is_file", return_value=True):
            metronome = Metronome(120)
            metronome.start()
            with patch("builtins.print") as mock_print:
                metronome.stop()
                self.assertFalse(metronome.is_running)
                mock_print.assert_any_call(f"{CURRENT_LANG['METRONOME_STOPPED_MSG']}")

if __name__ == "__main__":
    unittest.main()
