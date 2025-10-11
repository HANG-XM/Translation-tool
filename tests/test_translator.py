# tests/test_translator.py
import unittest
from unittest.mock import Mock, patch
from src.translator import BaiduTranslator, TranslationCache, TextPreprocessor

class TestTranslationCache(unittest.TestCase):
    def setUp(self):
        self.cache = TranslationCache(max_size=2, timeout=3600)
    
    def test_cache_set_and_get(self):
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
    
    def test_cache_size_limit(self):
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        self.assertIsNone(self.cache.get("key1"))

class TestTextPreprocessor(unittest.TestCase):
    def test_clean_text(self):
        text = "Hello|World[]O"
        cleaned = TextPreprocessor.clean_text(text)
        self.assertEqual(cleaned, "HelloIWorld00")

class TestBaiduTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = BaiduTranslator("test_appid", "test_appkey")
    
    @patch('requests.Session.get')
    def test_translate_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'trans_result': [{'dst': '测试结果'}]
        }
        mock_get.return_value = mock_response
        
        result = self.translator.translate("test", "en", "zh")
        self.assertEqual(result, "测试结果")
