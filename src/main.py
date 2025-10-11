import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
import os
import logging
import configparser
from datetime import datetime
import time
from settings_manager import SettingsManager
from ui_manager import UIManager
import sys
import logging.handlers
def get_base_path():
    """获取程序运行的基础路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        return os.path.dirname(sys.executable)
    else:
        # 如果是源码运行
        return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = get_base_path()
    return os.path.join(base_path, relative_path)

def setup_logging():
    base_path = get_base_path()
    log_dir = os.path.join(base_path, 'log')
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f'translator_{datetime.now().strftime("%Y%m%d")}.log')
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 使用RotatingFileHandler进行日志轮转
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
def check_directories():
    """检查并创建必要的目录"""
    try:
        base_path = get_base_path()
        log_dir = os.path.join(base_path, 'log')
        data_dir = os.path.join(base_path, 'data')
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    except Exception as e:
        Messagebox.showerror("错误", f"创建目录失败: {str(e)}")
        raise

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("翻译工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        base_path = get_base_path()
        self.config_file = os.path.join(base_path, 'data', 'config.ini')
        self.settings_manager = SettingsManager(self.root, self.config_file)
        
        setup_logging()
        check_directories()
        
        self.ui_manager = UIManager(self.root, self.settings_manager)
        self.settings_manager.set_theme('flatly')  # 修改为与ttkbootstrap主题名称一致
        self.ui_manager.load_config()
        self.ui_manager.bind_shortcuts()

def main():
    try:
        root = tb.Window(themename="flatly")
        app = TranslatorApp(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"程序启动失败: {str(e)}")
        Messagebox.show_error("错误", f"程序启动失败: {str(e)}")

if __name__ == '__main__':
    main()
