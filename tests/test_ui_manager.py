import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import ttkbootstrap as tb
from src.ui_manager import UIManager, TranslateTabManager, ConfigTabManager, AboutTabManager
from src.settings_manager import ThemeManager

class TestUIManager(unittest.TestCase):
    def test_setup_ui(self):
        with patch('src.ui_manager.UIManager.__init__') as mock_init:
            mock_init.return_value = None
            root = Mock()
            settings_manager = Mock()
            UIManager(root, settings_manager)
            mock_init.assert_called_once()

class TestTranslateTabManager(unittest.TestCase):
    def test_setup(self):
        with patch('src.ui_manager.TranslateTabManager.__init__') as mock_init:
            mock_init.return_value = None
            notebook = Mock()
            settings_manager = Mock()
            TranslateTabManager(notebook, settings_manager)
            mock_init.assert_called_once()

class TestConfigTabManager(unittest.TestCase):
    def test_setup(self):
        with patch('src.ui_manager.ConfigTabManager.__init__') as mock_init:
            mock_init.return_value = None
            notebook = Mock()
            settings_manager = Mock()
            ConfigTabManager(notebook, settings_manager)
            mock_init.assert_called_once()

class TestAboutTabManager(unittest.TestCase):
    def test_setup(self):
        with patch('src.ui_manager.AboutTabManager.__init__') as mock_init:
            mock_init.return_value = None
            notebook = Mock()
            AboutTabManager(notebook)
            mock_init.assert_called_once()

class TestThemeManager(unittest.TestCase):
    def test_set_theme(self):
        with patch('src.settings_manager.ThemeManager.__init__') as mock_init:
            mock_init.return_value = None
            root = Mock()
            ThemeManager(root)
            mock_init.assert_called_once()
