# tests/performance/test_translation_performance.py
import unittest
import time
import threading
from src.translator import BaiduTranslator

class TestTranslationPerformance(unittest.TestCase):
    def setUp(self):
        self.translator = BaiduTranslator("test_appid", "test_appkey")
    
    def test_concurrent_translation(self):
        def translate_task():
            self.translator.translate("test text")
        
        start_time = time.time()
        threads = []
        for _ in range(10):
            t = threading.Thread(target=translate_task)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        end_time = time.time()
        self.assertLess(end_time - start_time, 5)  # 应在5秒内完成
