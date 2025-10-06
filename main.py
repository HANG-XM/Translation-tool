import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
import os
import logging
import configparser
from datetime import datetime
from settings_manager import SettingsManager
from ui_manager import UIManager

def setup_logging():
    """设置日志记录"""
    log_file = os.path.join('log', f'translator_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 创建日志格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    
    # 配置根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def check_directories():
    """检查并创建必要的目录"""
    try:
        if not os.path.exists('log'):
            os.makedirs('log')
            
        if not os.path.exists('data'):
            os.makedirs('data')
    except Exception as e:
        Messagebox.showerror("错误", f"创建目录失败: {str(e)}")
        raise

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("翻译工具")
        # 修改窗口大小和最小尺寸
        self.root.geometry("1000x700")  # 增大窗口尺寸
        self.root.minsize(800, 600)     # 设置最小窗口尺寸
        
        # 初始化管理器
        self.config_file = os.path.join('data', 'config.ini')
        self.settings_manager = SettingsManager(self.root, self.config_file)
        
        # 设置日志
        setup_logging()
        
        # 检查并创建必要目录
        check_directories()
        
        # 设置界面
        self.ui_manager = UIManager(self.root, self.settings_manager)
        self.settings_manager.set_theme('light')  # 默认主题
        
        # 尝试加载配置
        self.ui_manager.load_config()

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
