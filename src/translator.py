import requests
import random
import hashlib
import json
import time
import logging
from collections import OrderedDict
from urllib3.util.retry import Retry
import threading

class TranslationCache:
    """翻译结果缓存管理"""
    def __init__(self, max_size=1000, timeout=7200):
        self._cache = OrderedDict()
        self._cache_size = max_size
        self._cache_timeout = timeout
        self._lock = threading.Lock()
        self._history = OrderedDict()
        self._max_history = 100

    def get(self, key):
        """获取缓存"""
        with self._lock:
            if key in self._cache:
                cached_time, cached_result = self._cache[key]
                if time.time() - cached_time < self._cache_timeout:
                    self._cache.move_to_end(key)
                    return cached_result
                else:
                    del self._cache[key]
            return None

    def set(self, key, value):
        """设置缓存"""
        with self._lock:
            current_time = time.time()
            if len(self._cache) >= self._cache_size:
                self._cache.popitem(last=False)
            self._cache[key] = (current_time, value)
            self._cache.move_to_end(key)

    def add_to_history(self, source_text, target_text, from_lang, to_lang):
        """添加翻译记录到历史"""
        with self._lock:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            history_key = f"{current_time}_{hash(source_text)}"
            
            self._history[history_key] = {
                'source_text': source_text,
                'target_text': target_text,
                'from_lang': from_lang,
                'to_lang': to_lang,
                'time': current_time
            }
            
            if len(self._history) > self._max_history:
                self._history.popitem(last=False)

    def get_history(self):
        """获取翻译历史"""
        with self._lock:
            return list(self._history.values())

    def clear_history(self):
        """清空翻译历史"""
        with self._lock:
            self._history.clear()
    def add_to_history(self, source_text, target_text, from_lang, to_lang, save_callback=None):
        """添加翻译记录到历史"""
        with self._lock:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            history_key = f"{current_time}_{hash(source_text)}"
            
            self._history[history_key] = {
                'source_text': source_text,
                'target_text': target_text,
                'from_lang': from_lang,
                'to_lang': to_lang,
                'time': current_time
            }
            
            if len(self._history) > self._max_history:
                self._history.popitem(last=False)
                
            # 立即保存到文件
            if save_callback:
                save_callback(self._history)
class TextPreprocessor:
    """文本预处理工具"""
    @staticmethod
    def clean_text(text):
        """清理OCR识别可能产生的特殊字符"""
        text = text.replace('|', 'I').replace('[]', '0').replace('O', '0')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

class BaiduTranslator:
    def __init__(self, appid, appkey):
        self.appid = appid
        self.appkey = appkey
        self.api_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        self.session = requests.Session()
        self.timeout = 10
        self.cache = TranslationCache()
        self.preprocessor = TextPreprocessor()
        
        self._init_session()
    
    def _init_session(self):
        """初始化会话配置"""
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=30,  # 增加连接池大小
            pool_maxsize=30,
            max_retries=retry_strategy
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',  # 启用HTTP keep-alive
        })

    def translate(self, query, from_lang='auto', to_lang='zh'):
        """翻译文本"""
        query = self.preprocessor.clean_text(query)
        if not query.strip():
            return "请输入要翻译的文本"

        cache_key = f"{from_lang}:{to_lang}:{query}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        result = self._request_translation(query, from_lang, to_lang)
        if result:
            self.cache.set(cache_key, result)
        return result

    def _request_translation(self, query, from_lang, to_lang):
        """请求翻译API"""
        if not self.appid or not self.appkey:
            return "请先配置API密钥"
            
        salt = str(random.randint(32768, 65536))
        sign = hashlib.md5(f"{self.appid}{query}{salt}{self.appkey}".encode()).hexdigest()
        
        params = {
            'q': query,
            'from': from_lang,
            'to': to_lang,
            'appid': self.appid,
            'salt': salt,
            'sign': sign
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if 'error_code' in result:
                return f"翻译错误: {result.get('error_msg', '未知错误')}"
            
            trans_result = result.get('trans_result', [])
            if not trans_result:
                return "未获取到翻译结果"
            
            return '\n'.join(item['dst'] for item in trans_result if 'dst' in item)
            
        except Exception as e:
            return f"翻译失败: {str(e)}"
