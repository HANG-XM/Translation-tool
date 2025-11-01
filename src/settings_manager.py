import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox

import time
import os
import configparser
import threading
import logging
import json
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

class ConfigManager:
    """配置文件管理"""
    def __init__(self, config_file):
        self.config_file = config_file
        self._config_lock = threading.Lock()
        self._config_cache = None
        self._config_cache_time = 0
        self._config_cache_timeout = 10
        self._executor = ThreadPoolExecutor(max_workers=2)
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
    @lru_cache(maxsize=32)
    def load_config(self):
        """加载配置"""
        current_time = time.time()
        if (self._config_cache is not None and 
            current_time - self._config_cache_time < self._config_cache_timeout):
            return self._config_cache
            
        if not os.path.exists(self.config_file):
            return None, None

        try:
            with self._config_lock:
                config = configparser.ConfigParser()
                # 使用线程安全的读取方式
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config.read_file(f)
                
                if 'BaiduAPI' in config:
                    appid = config['BaiduAPI'].get('appid', '')
                    appkey = config['BaiduAPI'].get('appkey', '')
                    self._update_cache(appid, appkey)
                    return appid, appkey
                
                return None, None
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
            return None, None
    
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
            current_time - self._config_cache_time < self._config_cache_timeout):
            return self._config_cache
            
        if not os.path.exists(self.config_file):
            return None, None

        try:
            with self._config_lock:
                config = configparser.ConfigParser()
                # 使用线程安全的读取方式
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config.read_file(f)
                
                if 'BaiduAPI' in config:
                    appid = config['BaiduAPI'].get('appid', '')
                    appkey = config['BaiduAPI'].get('appkey', '')
                    self._update_cache(appid, appkey)
                    return appid, appkey
                
                return None, None
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
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
            # 检查是否在主线程
            if not threading.current_thread() is threading.main_thread():
                # 如果不在主线程，将操作放回主线程
                self.root.after(0, lambda: self._set_theme_in_main_thread(theme))
                return
                
            self._set_theme_in_main_thread(theme)
        except Exception as e:
            logging.error(f"设置主题失败: {str(e)}")
            raise
            
    def _set_theme_in_main_thread(self, theme):
        """在主线程中设置主题"""
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
        # 添加历史记录文件路径
        base_path = os.path.dirname(config_file)
        self.history_file = os.path.join(base_path, 'history.json')
    
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

    def save_all_config(self, appid, appkey, shortcuts, theme, source_lang=None, target_lang=None, format_type=None, export_format=None):
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
            if format_type:
                config['Format'] = {'format_type': format_type}
            if export_format:
                config['Export'] = {'export_format': export_format}
            
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

    def load_export_format(self):
        """加载导出格式配置"""
        try:
            if not os.path.exists(self.config_manager.config_file):
                return 'txt'
            
            config = configparser.ConfigParser()
            config.read(self.config_manager.config_file, encoding='utf-8')
            
            if 'Export' in config:
                return config['Export'].get('export_format', 'txt')
            return 'txt'
        except Exception as e:
            logging.error(f"加载导出格式配置失败: {str(e)}")
            return 'txt'

    def load_format_type(self):
        """加载格式化配置"""
        try:
            if not os.path.exists(self.config_manager.config_file):
                return 'none'
            
            config = configparser.ConfigParser()
            config.read(self.config_manager.config_file, encoding='utf-8')
            
            if 'Format' in config:
                return config['Format'].get('format_type', 'none')
            return 'none'
        except Exception as e:
            logging.error(f"加载格式化配置失败: {str(e)}")
            return 'none'
    
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

    def save_translation_history(self, history):
        """保存翻译历史记录到独立文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # 使用临时文件确保数据完整性
            temp_file = self.history_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            # 原子性替换文件
            os.replace(temp_file, self.history_file)
            return True
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            logging.error(f"保存翻译历史失败: {str(e)}")
            raise e

    def load_translation_history(self):
        """从独立文件加载翻译历史记录"""
        try:
            if not os.path.exists(self.history_file):
                return {}
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"加载翻译历史失败: {str(e)}")
            return {}
    def save_translation_stats(self, stats):
        """保存翻译统计数据"""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_manager.config_file, encoding='utf-8')
            config['Stats'] = stats
            
            temp_file = self.config_manager.config_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                config.write(f)
            os.replace(temp_file, self.config_manager.config_file)
            return True
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            logging.error(f"保存翻译统计失败: {str(e)}")
            return False

    def load_translation_stats(self):
        """加载翻译统计数据"""
        try:
            if not os.path.exists(self.config_manager.config_file):
                return {
                    'total_translations': 0,
                    'total_characters': 0,
                    'daily_translations': 0,
                    'daily_characters': 0,
                    'last_reset_date': time.strftime('%Y-%m-%d')
                }
            
            config = configparser.ConfigParser()
            config.read(self.config_manager.config_file, encoding='utf-8')
            
            if 'Stats' in config:
                stats = dict(config['Stats'])
                # 检查是否需要重置每日统计
                current_date = time.strftime('%Y-%m-%d')
                if stats.get('last_reset_date') != current_date:
                    stats['daily_translations'] = 0
                    stats['daily_characters'] = 0
                    stats['last_reset_date'] = current_date
                    self.save_translation_stats(stats)
                return stats
            return {
                'total_translations': 0,
                'total_characters': 0,
                'daily_translations': 0,
                'daily_characters': 0,
                'last_reset_date': time.strftime('%Y-%m-%d')
            }
        except Exception as e:
            logging.error(f"加载翻译统计失败: {str(e)}")
            return {
                'total_translations': 0,
                'total_characters': 0,
                'daily_translations': 0,
                'daily_characters': 0,
                'last_reset_date': time.strftime('%Y-%m-%d')
            }