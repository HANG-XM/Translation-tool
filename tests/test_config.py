# tests/test_config.py
import os

# 测试配置
TEST_CONFIG = {
    'appid': 'test_appid',
    'appkey': 'test_appkey',
    'timeout': 10,
    'cache_size': 1000,
    'cache_timeout': 3600
}

# 测试数据路径
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

# 性能测试阈值
PERFORMANCE_THRESHOLDS = {
    'cache_operations': 2.0,  # 缓存操作时间阈值（秒）
    'translation_concurrent': 10.0,  # 并发翻译时间阈值（秒）
}
