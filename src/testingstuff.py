import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import unittest
from unittest.mock import patch, MagicMock
import pygame
from pathlib import Path
from metronome import Metronome, check_wav_file
from constants import SOUND_FILE, CURRENT_LANG
from io import StringIO
import sys

class TestMetronome(unittest.TestCase):
    def setUp(self):
        # Capture stdout
        self.held_output = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        # Restore stdout
        sys.stdout = self.old_stdout

    def test_pygame_hide_prompt(self):
        self.assertEqual(os.environ.get('PYGAME_HIDE_SUPPORT_PROMPT'), "hide")

    @patch('pygame.mixer.init')
    def test_metronome_init_success(self, mock_init):
        mock_init.return_value = None
        metronome = Metronome()
        mock_init.assert_called_once()
        self.assertEqual(self.held_output.getvalue(), "")

    @patch('pygame.mixer.init')
    def test_metronome_init_failure(self, mock_init):
        mock_init.side_effect = pygame.error
        metronome = Metronome()
        mock_init.assert_called_once()
        self.assertEqual(self.held_output.getvalue(), CURRENT_LANG["PYMIXER_ERROR"] + "\n")

    def test_check_wav_file_when_file_exists(self):
        with patch.object(Path, 'is_file', return_value=True):
            self.assertTrue(check_wav_file())
            self.assertEqual(self.held_output.getvalue(), "")

    def test_check_wav_file_when_file_not_exists(self):
        with patch.object(Path, 'is_file', return_value=False):
            self.assertFalse(check_wav_file())
            self.assertEqual(self.held_output.getvalue(), "")

    @patch('pygame.mixer.Sound')
    @patch('metronome.check_wav_file', return_value=True)
    def test_load_sound_success(self, mock_check, mock_sound):
        metronome = Metronome()
        result = metronome.load_sound()
        self.assertTrue(result)
        mock_check.assert_called_once()
        mock_sound.assert_called_once_with(SOUND_FILE)
        self.assertEqual(self.held_output.getvalue(), "")

    @patch('metronome.check_wav_file', return_value=False)
    def test_load_sound_failure(self, mock_check):
        metronome = Metronome()
        result = metronome.load_sound()
        self.assertFalse(result)
        mock_check.assert_called_once()
        self.assertEqual(self.held_output.getvalue(), CURRENT_LANG["NOWAVE_FILE"] + "\n")

if __name__ == '__main__':
    unittest.main()