# tests/performance/test_cache_performance.py
import unittest
import time
from src.translator import TranslationCache

class TestCachePerformance(unittest.TestCase):
    def test_cache_performance(self):
        cache = TranslationCache(max_size=1000, timeout=3600)
        
        start_time = time.time()
        for i in range(1000):
            cache.set(f"key{i}", f"value{i}")
        
        for i in range(1000):
            cache.get(f"key{i}")
        
        end_time = time.time()
        self.assertLess(end_time - start_time, 1)  # 应在1秒内完成