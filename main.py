import requests
import random
import hashlib
import json
from urllib.parse import quote
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import configparser

class BaiduTranslator:
    def __init__(self, appid, appkey):
        self.appid = appid
        self.appkey = appkey
        self.api_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        
    def translate(self, query, from_lang='auto', to_lang='zh'):
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
            response = requests.get(self.api_url, params=params)
            result = response.json()
            
            if 'error_code' in result:
                return f"翻译错误: {result.get('error_msg', '未知错误')}"
            
            trans_result = result.get('trans_result', [])
            if not trans_result:
                return "未获取到翻译结果"
            
            translations = [item['dst'] for item in trans_result]
            return '\n'.join(translations)
            
        except Exception as e:
            return f"请求失败: {str(e)}"

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("翻译工具")
        self.root.geometry("800x600")
        
        # 初始化变量
        self.translator = None
        self.config_file = os.path.join('data', 'config.ini')
        
        # 检查并创建必要目录
        self.check_directories()
        
        # 设置界面
        self.setup_ui()
        
        # 尝试加载配置
        self.load_config()
        
    def check_directories(self):
        """检查并创建必要的目录"""
        # 检查并创建log目录
        if not os.path.exists('log'):
            os.makedirs('log')
            
        # 检查并创建data目录
        if not os.path.exists('data'):
            os.makedirs('data')

    def setup_ui(self):
        # 配置框架
        config_frame = ttk.LabelFrame(self.root, text="配置信息", padding=10)
        config_frame.pack(padx=10, pady=5, fill=tk.X)
        
        # APPID 输入框
        ttk.Label(config_frame, text="APPID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.appid_entry = ttk.Entry(config_frame, width=50)
        self.appid_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # APPKEY 输入框
        ttk.Label(config_frame, text="APPKEY:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.appkey_entry = ttk.Entry(config_frame, width=50, show="*")  # 使用*号显示密码
        self.appkey_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 保存配置按钮
        save_btn = ttk.Button(config_frame, text="保存配置", command=self.save_config)
        save_btn.grid(row=1, column=2, padx=20, pady=5)
        
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
        
    def save_config(self):
        """保存配置到文件"""
        appid = self.appid_entry.get().strip()
        appkey = self.appkey_entry.get().strip()
        
        if not appid or not appkey:
            messagebox.showerror("错误", "请输入APPID和APPKEY")
            return
            
        # 创建配置解析器
        config = configparser.ConfigParser()
        config['BaiduAPI'] = {
            'appid': appid,
            'appkey': appkey
        }
        
        try:
            # 保存配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            # 更新翻译器实例
            self.translator = BaiduTranslator(appid, appkey)
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            
    def load_config(self):
        """从文件加载配置"""
        if not os.path.exists(self.config_file):
            return
            
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file, encoding='utf-8')
            
            if 'BaiduAPI' in config:
                appid = config['BaiduAPI'].get('appid', '')
                appkey = config['BaiduAPI'].get('appkey', '')
                
                # 填充到输入框
                self.appid_entry.delete(0, tk.END)
                self.appid_entry.insert(0, appid)
                
                self.appkey_entry.delete(0, tk.END)
                self.appkey_entry.insert(0, appkey)
                
                # 如果有配置，创建翻译器实例
                if appid and appkey:
                    self.translator = BaiduTranslator(appid, appkey)
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")
        
    def translate(self):
        if not self.translator:
            messagebox.showerror("错误", "请先保存配置")
            return
            
        source_text = self.source_text.get("1.0", tk.END).strip()
        if not source_text:
            messagebox.showwarning("警告", "请输入要翻译的文本")
            return
            
        try:
            result = self.translator.translate(source_text)
            self.target_text.delete("1.0", tk.END)
            self.target_text.insert("1.0", result)
        except Exception as e:
            messagebox.showerror("错误", f"翻译失败: {str(e)}")
            
    def clear_text(self):
        self.source_text.delete("1.0", tk.END)
        self.target_text.delete("1.0", tk.END)
            

def main():
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
