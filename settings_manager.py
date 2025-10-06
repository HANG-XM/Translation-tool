import os
import configparser
import threading
import logging
import time
from ttkbootstrap.dialogs import Messagebox

class SettingsManager:
    def __init__(self, root, config_file):
        self.root = root
        self.config_file = config_file
        self._config_lock = threading.Lock()
        self._config_cache = None  # 添加配置缓存
        self._config_cache_time = 0  # 配置缓存时间
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
    def save_config(self, appid, appkey):
        """保存配置到文件"""
        try:
            if not appid or not appkey:
                Messagebox.show_error("错误", "请输入APPID和APPKEY")
                return False
                
            with self._config_lock:
                config = configparser.ConfigParser()
                config['BaiduAPI'] = {
                    'appid': appid,
                    'appkey': appkey
                }
                
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                
                temp_file = self.config_file + '.tmp'
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        config.write(f)
                    os.replace(temp_file, self.config_file)
                    # 更新缓存
                    self._config_cache = (appid, appkey)
                    self._config_cache_time = time.time()
                except Exception as e:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                    raise e
            
            return True

        except Exception as e:
            Messagebox.show_error("错误", f"保存配置失败: {str(e)}")
            return False
            
    def load_config(self):
        """从文件加载配置（带缓存）"""
        try:
            current_time = time.time()
            # 如果缓存存在且未过期（5秒内），直接返回缓存
            if (self._config_cache is not None and 
                current_time - self._config_cache_time < 5):
                return self._config_cache
                
            if not os.path.exists(self.config_file):
                return None, None
                
            config = configparser.ConfigParser()
            config.read(self.config_file, encoding='utf-8')
            
            if 'BaiduAPI' in config:
                appid = config['BaiduAPI'].get('appid', '')
                appkey = config['BaiduAPI'].get('appkey', '')
                # 更新缓存
                self._config_cache = (appid, appkey)
                self._config_cache_time = current_time
                return appid, appkey
            
            return None, None
        except Exception as e:
            Messagebox.show_error("错误", f"加载配置失败: {str(e)}")
            return None, None
            
    def set_theme(self, theme):
        """设置主题"""
        try:
            geometry = self.root.geometry()
            
            if theme == '黑夜':
                self.root.style.theme_use('darkly')
                self.root.configure(background='#2b2b2b')
            else:
                self.root.style.theme_use('flatly')
                self.root.configure(background='#ffffff')
            
            self.root.geometry(geometry)
            self.root.update_idletasks()
            self.root.event_generate('<Configure>')
        except Exception as e:
            logging.error(f"设置主题失败: {str(e)}")
