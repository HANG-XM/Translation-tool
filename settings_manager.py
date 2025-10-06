import os
import configparser
import threading
import logging
import time
from ttkbootstrap.dialogs import Messagebox
import ttkbootstrap as tb

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
    
    def save_shortcuts(self, shortcuts):
        """保存快捷键配置"""
        try:
            config = configparser.ConfigParser()
            config['Shortcuts'] = shortcuts
            
            temp_file = self.config_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                config.write(f)
            os.replace(temp_file, self.config_file)
            return True
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e

    def load_shortcuts(self):
        """加载快捷键配置"""
        if not os.path.exists(self.config_file):
            return {
                'translate': '<Control-Return>',
                'clear': '<Control-d>',
                'capture': '<Control-s>'
            }
        
        config = configparser.ConfigParser()
        config.read(self.config_file, encoding='utf-8')
        
        if 'Shortcuts' in config:
            return dict(config['Shortcuts'])
        return {
            'translate': '<Control-Return>',
            'clear': '<Control-d>',
            'capture': '<Control-s>'
        }
    
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
            # 保存当前窗口状态
            geometry = self.root.geometry()
            current_tab = None
            
            # 获取当前选中的标签页
            for child in self.root.winfo_children():
                if isinstance(child, tb.Notebook):
                    current_tab = child.index(child.select())
                    break
            
            # 切换主题
            if theme == '黑夜':
                self.root.style.theme_use('darkly')
            else:
                self.root.style.theme_use('flatly')
            
            # 恢复窗口状态
            self.root.geometry(geometry)
            if current_tab is not None:
                self.root.after(100, lambda: child.select(current_tab))
                
            self.root.update_idletasks()
        except Exception as e:
            logging.error(f"设置主题失败: {str(e)}")
            raise

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
    
    def save_shortcuts(self, shortcuts):
        """保存快捷键配置"""
        try:
            return self.config_manager.save_shortcuts(shortcuts)
        except Exception as e:
            Messagebox.show_error("错误", f"保存快捷键失败: {str(e)}")
            return False
    
    def load_shortcuts(self):
        """加载快捷键配置"""
        try:
            return self.config_manager.load_shortcuts()
        except Exception as e:
            Messagebox.show_error("错误", f"加载快捷键失败: {str(e)}")
            return {
                'translate': '<Control-Return>',
                'clear': '<Control-d>',
                'capture': '<Control-s>'
            }
    
    def set_theme(self, theme):
        """设置主题"""
        self.theme_manager.set_theme(theme)

    def save_all_config(self, appid, appkey, shortcuts, theme, source_lang=None, target_lang=None):
        """保存所有配置"""
        try:
            config = configparser.ConfigParser()
            config['BaiduAPI'] = {'appid': appid, 'appkey': appkey}
            config['Shortcuts'] = shortcuts
            config['Theme'] = {'theme': theme}
            if source_lang and target_lang:
                config['Languages'] = {
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
            
            temp_file = self.config_manager.config_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                config.write(f)
            os.replace(temp_file, self.config_manager.config_file)
            
            # 应用主题设置
            self.set_theme(theme)
            return True
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e
    
    def load_theme(self):
        """加载主题配置"""
        try:
            if not os.path.exists(self.config_manager.config_file):
                return '白天'
            
            config = configparser.ConfigParser()
            config.read(self.config_manager.config_file, encoding='utf-8')
            
            if 'Theme' in config:
                return config['Theme'].get('theme', '白天')
            return '白天'
        except Exception as e:
            logging.error(f"加载主题配置失败: {str(e)}")
            return '白天'
        
    def save_languages(self, source_lang, target_lang):
        """保存语言设置"""
        try:
            config = configparser.ConfigParser()
            config['Languages'] = {
                'source_lang': source_lang,
                'target_lang': target_lang
            }
            
            temp_file = self.config_manager.config_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                config.write(f)
            os.replace(temp_file, self.config_manager.config_file)
            return True
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e

    def load_languages(self):
        """加载语言设置"""
        try:
            if not os.path.exists(self.config_manager.config_file):
                return '自动检测', '英语'
            
            config = configparser.ConfigParser()
            config.read(self.config_manager.config_file, encoding='utf-8')
            
            if 'Languages' in config:
                return (
                    config['Languages'].get('source_lang', '自动检测'),
                    config['Languages'].get('target_lang', '英语')
                )
            return '自动检测', '英语'
        except Exception as e:
            logging.error(f"加载语言设置失败: {str(e)}")
            return '自动检测', '英语'