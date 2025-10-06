import os
import configparser
import threading
import logging
import time
from ttkbootstrap.dialogs import Messagebox

class ConfigManager:
    """配置文件管理"""
    def __init__(self, config_file):
        self.config_file = config_file
        self._config_lock = threading.Lock()
        self._config_cache = None
        self._config_cache_time = 0
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
    
    def save_config(self, appid, appkey):
        """保存配置"""
        if not appid or not appkey:
            return False
            
        with self._config_lock:
            config = configparser.ConfigParser()
            config['BaiduAPI'] = {'appid': appid, 'appkey': appkey}
            
            temp_file = self.config_file + '.tmp'
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                with open(temp_file, 'w', encoding='utf-8') as f:
                    config.write(f)
                os.replace(temp_file, self.config_file)
                self._update_cache(appid, appkey)
                return True
            except Exception as e:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise e
    
    def load_config(self):
        """加载配置"""
        current_time = time.time()
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
            self._update_cache(appid, appkey)
            return appid, appkey
        
        return None, None
    
    def _update_cache(self, appid, appkey):
        """更新配置缓存"""
        self._config_cache = (appid, appkey)
        self._config_cache_time = time.time()

class ThemeManager:
    """主题管理"""
    def __init__(self, root):
        self.root = root
    
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

class SettingsManager:
    """设置管理器"""
    def __init__(self, root, config_file):
        self.root = root
        self.config_manager = ConfigManager(config_file)
        self.theme_manager = ThemeManager(root)
    
    def save_config(self, appid, appkey):
        """保存配置"""
        try:
            return self.config_manager.save_config(appid, appkey)
        except Exception as e:
            Messagebox.show_error("错误", f"保存配置失败: {str(e)}")
            return False
    
    def load_config(self):
        """加载配置"""
        try:
            return self.config_manager.load_config()
        except Exception as e:
            Messagebox.show_error("错误", f"加载配置失败: {str(e)}")
            return None, None
    
    def set_theme(self, theme):
        """设置主题"""
        self.theme_manager.set_theme(theme)
