import requests
import random
import hashlib
import json
import time
import logging
from collections import OrderedDict

class BaiduTranslator:
    def __init__(self, appid, appkey):
        self.appid = appid
        self.appkey = appkey
        self.api_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        self.session = requests.Session()
        self.timeout = 10
        
        # 优化连接池配置
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=3,
            backoff_factor=0.5
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })

        # 使用有序字典实现LRU缓存
        self._cache = OrderedDict()
        self._cache_size = 100
        self._cache_timeout = 3600
        
    def translate(self, query, from_lang='auto', to_lang='zh'):
        if not query.strip():
            return "请输入要翻译的文本"

        # 检查缓存
        cache_key = f"{from_lang}:{to_lang}:{query}"
        current_time = time.time()

        # 检查缓存是否存在且未过期
        if cache_key in self._cache:
            cached_time, cached_result = self._cache[cache_key]
            if time.time() - cached_time < self._cache_timeout:
                logging.info(f"使用缓存结果: {query} -> {cached_result}")
                # 将使用的项移到末尾
                self._cache.move_to_end(cache_key)
                return cached_result
            else:
                # 缓存过期，删除
                del self._cache[cache_key]
                logging.info(f"缓存已过期，删除缓存: {cache_key}")

        salt = str(random.randint(32768, 65536))
        sign_str = self.appid + query + salt + self.appkey
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        
        params = {
            'q': query,
            'from': from_lang,
            'to': to_lang,
            'appid': self.appid,
            'salt': salt,
            'sign': sign
        }
        
        request_url = f"{self.api_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        logging.info(f"发送翻译请求: {request_url}")

        try:
            response = self.session.get(self.api_url, params=params, timeout=self.timeout)
            logging.info(f"收到响应状态码: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()

            logging.info(f"收到响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                logging.error(f"翻译API错误: {error_msg}")
                return f"翻译错误: {error_msg}"
            
            trans_result = result.get('trans_result', [])
            if not trans_result:
                logging.warning("未获取到翻译结果")
                return "未获取到翻译结果"
            
            translations = []
            for item in trans_result:
                if 'dst' in item:
                    translations.append(item['dst'])
                    logging.info(f"翻译结果项: {item}")
            
            if not translations:
                logging.warning("未获取到有效的翻译结果")
                return "未获取到有效的翻译结果"
                
            result_text = '\n'.join(translations)
            logging.info(f"翻译完成: {query} -> {result_text}")
            
            # LRU缓存更新逻辑
            if len(self._cache) >= self._cache_size:
                self._cache.popitem(last=False)  # 移除最久未使用的项
            self._cache[cache_key] = (current_time, result_text)
            self._cache.move_to_end(cache_key)  # 将使用的项移到末尾
            logging.info(f"缓存翻译结果: {cache_key}")
            
            return result_text
            
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            logging.error(error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = f"解析响应失败: {str(e)}"
            logging.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            logging.error(error_msg)
            return error_msg
