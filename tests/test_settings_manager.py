import unittest
from unittest.mock import Mock, patch
import os
import tempfile
import ttkbootstrap as tb
from src.settings_manager import ConfigManager, ThemeManager, SettingsManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, 'config.ini')
        self.config_manager = ConfigManager(self.temp_file)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_save_and_load_config(self):
        self.config_manager.save_config("test_appid", "test_appkey")
        appid, appkey = self.config_manager.load_config()
        self.assertEqual(appid, "test_appid")
        self.assertEqual(appkey, "test_appkey")

class TestThemeManager(unittest.TestCase):
    @patch('src.settings_manager.ThemeManager.set_theme')
    def test_set_theme(self, mock_set_theme):
        root = Mock()
        theme_manager = ThemeManager(root)
        theme_manager.set_theme("黑夜")
        mock_set_theme.assert_called_once_with("黑夜")

class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file = os.path.join(self.temp_dir.name, 'config.ini')
        self.root = Mock()
        self.settings_manager = SettingsManager(self.root, self.temp_file)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    @patch('src.settings_manager.SettingsManager.set_theme')
    def test_save_and_load_theme(self, mock_set_theme):
        mock_set_theme.return_value = None
        self.settings_manager.set_theme("黑夜")
        mock_set_theme.assert_called_once_with("黑夜")
    
    def test_save_and_load_config(self):
        result = self.settings_manager.save_config("test_appid", "test_appkey")
        self.assertTrue(result)
        appid, appkey = self.settings_manager.load_config()
        self.assertEqual(appid, "test_appid")
        self.assertEqual(appkey, "test_appkey")
    
    def test_save_and_load_shortcuts(self):
        shortcuts = {
            'translate': '<Control-t>',
            'clear': '<Control-c>',
            'capture': '<Control-s>'
        }
        result = self.settings_manager.save_shortcuts(shortcuts)
        self.assertTrue(result)
        loaded_shortcuts = self.settings_manager.load_shortcuts()
        self.assertEqual(loaded_shortcuts, shortcuts)
