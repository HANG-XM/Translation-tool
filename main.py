import requests
import random
import hashlib
import json
from urllib.parse import quote
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import configparser
import logging
from datetime import datetime

class BaiduTranslator:
    def __init__(self, appid, appkey):
        self.appid = appid
        self.appkey = appkey
        self.api_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        self.session = requests.Session()
        self.timeout = 10
        
    def translate(self, query, from_lang='auto', to_lang='zh'):
        if not query.strip():
            return "请输入要翻译的文本"
            
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
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                logging.error(f"翻译API错误: {error_msg}")
                return f"翻译错误: {error_msg}"
            
            trans_result = result.get('trans_result', [])
            if not trans_result:
                logging.warning("未获取到翻译结果")
                return "未获取到翻译结果"
            
            translations = [item['dst'] for item in trans_result]
            return '\n'.join(translations)
            
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

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("翻译工具")
        self.root.geometry("800x600")
        
        # 初始化变量
        self.translator = None
        self.config_file = os.path.join('data', 'config.ini')
        
        # 设置日志
        self.setup_logging()
        
        # 检查并创建必要目录
        self.check_directories()
        
        # 设置界面
        self.setup_ui()
        
        # 尝试加载配置
        self.load_config()
        
    def setup_logging(self):
        """设置日志记录"""
        log_file = os.path.join('log', f'translator_{datetime.now().strftime("%Y%m%d")}.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
    def check_directories(self):
        """检查并创建必要的目录"""
        try:
            if not os.path.exists('log'):
                os.makedirs('log')
                logging.info("创建log目录")
                
            if not os.path.exists('data'):
                os.makedirs('data')
                logging.info("创建data目录")
        except Exception as e:
            logging.error(f"创建目录失败: {str(e)}")
            messagebox.showerror("错误", f"创建目录失败: {str(e)}")

    def setup_ui(self):
        """设置用户界面"""
        try:
            # 配置框架
            config_frame = ttk.Frame(self.root)
            config_frame.pack(padx=10, pady=5, fill=tk.X)
            
            # APPID 标签和输入框
            ttk.Label(config_frame, text="APPID:").pack(side=tk.LEFT, padx=5)
            self.appid_entry = ttk.Entry(config_frame, width=30)
            self.appid_entry.pack(side=tk.LEFT, padx=5)
            
            # APPKEY 标签和输入框
            ttk.Label(config_frame, text="APPKEY:").pack(side=tk.LEFT, padx=5)
            self.appkey_entry = ttk.Entry(config_frame, width=30, show="*")
            self.appid_entry.pack(side=tk.LEFT, padx=5)
            
            # 保存配置按钮
            save_btn = ttk.Button(config_frame, text="保存配置", command=self.save_config)
            save_btn.pack(side=tk.LEFT, padx=20)
            
            # 语言选择框架
            lang_frame = ttk.Frame(self.root)
            lang_frame.pack(padx=10, pady=5, fill=tk.X)
            
            # 源语言选择
            ttk.Label(lang_frame, text="源语言:").pack(side=tk.LEFT, padx=5)
            self.source_lang = ttk.Combobox(lang_frame, width=15, state="readonly")
            self.source_lang['values'] = ('自动检测', '中文', '英语', '日语', '韩语', '法语', '德语', '俄语', '西班牙语')
            self.source_lang.set('自动检测')
            self.source_lang.pack(side=tk.LEFT, padx=5)
            
            # 目标语言选择
            ttk.Label(lang_frame, text="目标语言:").pack(side=tk.LEFT, padx=5)
            self.target_lang = ttk.Combobox(lang_frame, width=15, state="readonly")
            self.target_lang['values'] = ('中文', '英语', '日语', '韩语', '法语', '德语', '俄语', '西班牙语')
            self.target_lang.set('英语')
            self.target_lang.pack(side=tk.LEFT, padx=5)
            
            # 源文本框架
            source_frame = ttk.LabelFrame(self.root, text="源文本", padding=5)
            source_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            
            # 源文本编辑框
            self.source_text = scrolledtext.ScrolledText(source_frame, wrap=tk.WORD, width=80, height=10)
            self.source_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
            
            # 操作按钮框架
            button_frame = ttk.Frame(self.root)
            button_frame.pack(padx=10, pady=5, fill=tk.X)
            
            # 翻译按钮
            self.translate_btn = ttk.Button(button_frame, text="翻译", command=self.translate)
            self.translate_btn.pack(side=tk.LEFT, padx=5)
            
            # 清空按钮
            clear_btn = ttk.Button(button_frame, text="清空", command=self.clear_text)
            clear_btn.pack(side=tk.LEFT, padx=5)
            
            # 目标文本框架
            target_frame = ttk.LabelFrame(self.root, text="翻译结果", padding=5)
            target_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
            
            # 目标文本编辑框
            self.target_text = scrolledtext.ScrolledText(target_frame, wrap=tk.WORD, width=80, height=10)
            self.target_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
            
            logging.info("界面初始化完成")
        except Exception as e:
            logging.error(f"界面初始化失败: {str(e)}")
            messagebox.showerror("错误", f"界面初始化失败: {str(e)}")
        
    def save_config(self):
        """保存配置到文件"""
        try:
            appid = self.appid_entry.get().strip()
            appkey = self.appkey_entry.get().strip()
            
            if not appid or not appkey:
                messagebox.showerror("错误", "请输入APPID和APPKEY")
                return
                
            config = configparser.ConfigParser()
            config['BaiduAPI'] = {
                'appid': appid,
                'appkey': appkey
            }
            
            os.makedirs('data', exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            self.translator = BaiduTranslator(appid, appkey)
            logging.info("配置保存成功")
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            
    def load_config(self):
        """从文件加载配置"""
        try:
            if not os.path.exists(self.config_file):
                logging.info("配置文件不存在")
                return
                
            config = configparser.ConfigParser()
            config.read(self.config_file, encoding='utf-8')
            
            if 'BaiduAPI' in config:
                appid = config['BaiduAPI'].get('appid', '')
                appkey = config['BaiduAPI'].get('appkey', '')
                
                self.appid_entry.delete(0, tk.END)
                self.appid_entry.insert(0, appid)
                
                self.appkey_entry.delete(0, tk.END)
                self.appkey_entry.insert(0, appkey)
                
                if appid and appkey:
                    self.translator = BaiduTranslator(appid, appkey)
                    logging.info("配置加载成功")
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")
        
    def translate(self):
        """执行翻译操作"""
        try:
            if not self.translator:
                messagebox.showerror("错误", "请先保存配置")
                return
                
            source_text = self.source_text.get("1.0", tk.END).strip()
            if not source_text:
                messagebox.showwarning("警告", "请输入要翻译的文本")
                return
            
            # 获取语言代码
            lang_map = {
                '自动检测': 'auto',
                '中文': 'zh',
                '英语': 'en',
                '日语': 'ja',
                '韩语': 'ko',
                '法语': 'fr',
                '德语': 'de',
                '俄语': 'ru',
                '西班牙语': 'es'
            }
            
            from_lang = lang_map[self.source_lang.get()]
            to_lang = lang_map[self.target_lang.get()]
            
            self.translate_btn.state(['disabled'])
            self.root.update()
            
            result = self.translator.translate(source_text, from_lang=from_lang, to_lang=to_lang)
            self.target_text.delete("1.0", tk.END)
            self.target_text.insert("1.0", result)
            
            logging.info("翻译操作完成")
        except Exception as e:
            logging.error(f"翻译操作失败: {str(e)}")
            messagebox.showerror("错误", f"翻译失败: {str(e)}")
        finally:
            self.translate_btn.state(['!disabled'])
            
    def clear_text(self):
        """清空文本框"""
        try:
            self.source_text.delete("1.0", tk.END)
            self.target_text.delete("1.0", tk.END)
            logging.info("清空文本框")
        except Exception as e:
            logging.error(f"清空文本框失败: {str(e)}")
            messagebox.showerror("错误", f"清空文本框失败: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = TranslatorApp(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"程序启动失败: {str(e)}")
        messagebox.showerror("错误", f"程序启动失败: {str(e)}")

if __name__ == '__main__':
    main()