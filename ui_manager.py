import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
import os
import time
from translator import BaiduTranslator
import tkinter as tk

class TitleBarManager:
    def __init__(self, root):
        self.root = root
        self.is_maximized = False
        self.normal_geometry = None
        self.title_bar = None
        self.max_btn = None
        
    def setup(self):
        """设置标题栏"""
        self.title_bar = tb.Frame(self.root, bootstyle=PRIMARY)
        self.title_bar.pack(fill="x")
        
        # 创建标题和控制按钮
        title_frame = tb.Frame(self.title_bar, bootstyle=PRIMARY)
        title_frame.pack(side="left", padx=10)
        control_frame = tb.Frame(self.title_bar, bootstyle=PRIMARY)
        control_frame.pack(side="right")

        # 添加标题和控制按钮组件
        title_label = tb.Label(title_frame, text="翻译工具", 
                             font=('微软雅黑', 10, 'bold'),
                             bootstyle="primary-inverse.TLabel")
        title_label.pack(side="left", padx=5)

        min_btn = tb.Button(control_frame, text="─", width=3,
                          bootstyle="primary.TButton",
                          command=self.root.iconify)
        min_btn.pack(side="left", padx=2)
        
        self.max_btn = tb.Button(control_frame, text="□", width=3,
                               bootstyle="primary.TButton",
                               command=self.toggle_maximize)
        self.max_btn.pack(side="left", padx=2)
        
        close_btn = tb.Button(control_frame, text="✕", width=3,
                            bootstyle="danger.TButton",
                            command=self.root.quit)
        close_btn.pack(side="left", padx=2)

        # 绑定拖动事件
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.on_move)
        title_label.bind('<Button-1>', self.start_move)
        title_label.bind('<B1-Motion>', self.on_move)

    def update_style(self, theme):
        """更新标题栏样式"""
        if theme == '黑夜':
            self.title_bar.configure(bootstyle='dark')
            self.max_btn.configure(bootstyle='dark.TButton')
            min_btn = self.title_bar.winfo_children()[1].winfo_children()[0]
            min_btn.configure(bootstyle='dark.TButton')
            close_btn = self.title_bar.winfo_children()[1].winfo_children()[2]
            close_btn.configure(bootstyle='danger.TButton')
        else:
            self.title_bar.configure(bootstyle='primary')
            self.max_btn.configure(bootstyle='primary.TButton')
            min_btn = self.title_bar.winfo_children()[1].winfo_children()[0]
            min_btn.configure(bootstyle='primary.TButton')
            close_btn = self.title_bar.winfo_children()[1].winfo_children()[2]
            close_btn.configure(bootstyle='danger.TButton')

    def start_move(self, event):
        """开始移动窗口"""
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        """移动窗口"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def toggle_maximize(self):
        """切换窗口最大化状态"""
        if not self.is_maximized:
            self.normal_geometry = self.root.geometry()
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            self.max_btn.config(text="❐")
            self.is_maximized = True
        else:
            self.root.geometry(self.normal_geometry)
            self.max_btn.config(text="□")
            self.is_maximized = False

class TranslateTabManager:
    def __init__(self, notebook, settings_manager):
        self.notebook = notebook
        self.settings_manager = settings_manager
        self.source_lang = None
        self.target_lang = None
        self.source_text = None
        self.target_text = None
        self.translate_btn = None
        self.clear_btn = None
        self.capture_btn = None
        
    def setup(self):
        """设置翻译标签页"""
        translate_frame = tb.Frame(self.notebook)
        self.notebook.add(translate_frame, text="📸 截图翻译")

        translate_frame.rowconfigure(1, weight=1)
        translate_frame.columnconfigure(0, weight=1)

        self._create_toolbar(translate_frame)
        self._create_text_areas(translate_frame)
        self._create_bottom_toolbar(translate_frame)

    def _create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = tb.Frame(parent, bootstyle=SECONDARY)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        lang_frame = tb.LabelFrame(toolbar, text="语言设置", padding=6, bootstyle=INFO)
        lang_frame.pack(side=TOP, padx=0, pady=0, fill=X)

        lang_grid = tb.Frame(lang_frame)
        lang_grid.pack(fill=X)
        lang_grid.columnconfigure(1, weight=1)
        lang_grid.columnconfigure(3, weight=1)

        tb.Label(lang_grid, text="源语言:", font=('微软雅黑', 9)).grid(row=0, column=0, padx=(5,2), pady=2, sticky=E)
        self.source_lang = tb.Combobox(lang_grid, width=12, state="readonly", bootstyle=INFO)
        self.source_lang['values'] = ('自动检测', '中文', '英语', '日语', '韩语', '法语', '德语', '俄语', '西班牙语')
        self.source_lang.set('自动检测')
        self.source_lang.grid(row=0, column=1, padx=(0,10), pady=2, sticky=W+E)

        tb.Label(lang_grid, text="目标语言:", font=('微软雅黑', 9)).grid(row=0, column=2, padx=(5,2), pady=2, sticky=E)
        self.target_lang = tb.Combobox(lang_grid, width=12, state="readonly", bootstyle=INFO)
        self.target_lang['values'] = ('中文', '英语', '日语', '韩语', '法语', '德语', '俄语', '西班牙语')
        self.target_lang.set('英语')
        self.target_lang.grid(row=0, column=3, padx=(0,5), pady=2, sticky=W+E)

    def _create_text_areas(self, parent):
        """创建文本区域"""
        text_container = tb.Frame(parent)
        text_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        text_container.rowconfigure(0, weight=1)
        text_container.columnconfigure(0, weight=1)

        paned_window = tb.PanedWindow(text_container, orient=VERTICAL)
        paned_window.pack(fill=BOTH, expand=True)

        source_frame = tb.LabelFrame(paned_window, text="源文本", padding=6, bootstyle=PRIMARY)
        paned_window.add(source_frame, weight=1)

        self.source_text = ScrolledText(source_frame, wrap="word", height=5, font=('微软雅黑', 10))
        self.source_text.pack(padx=4, pady=4, fill=BOTH, expand=True)

        target_frame = tb.LabelFrame(paned_window, text="翻译结果", padding=6, bootstyle=PRIMARY)
        paned_window.add(target_frame, weight=2)

        self.target_text = ScrolledText(target_frame, wrap="word", height=7, font=('微软雅黑', 10))
        self.target_text.pack(padx=4, pady=4, fill=BOTH, expand=True)

    def _create_bottom_toolbar(self, parent):
        """创建底部工具栏"""
        bottom_toolbar = tb.Frame(parent, bootstyle=SECONDARY)
        bottom_toolbar.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))

        button_frame = tb.LabelFrame(bottom_toolbar, text="操作", padding=6, bootstyle=INFO)
        button_frame.pack(side=TOP, padx=0, pady=0, fill=X)

        button_grid = tb.Frame(button_frame)
        button_grid.pack(fill=X)

        self.translate_btn = tb.Button(button_grid, text="🔤 翻译", 
                                    bootstyle=PRIMARY, width=10)
        self.translate_btn.grid(row=0, column=0, padx=6, pady=2, sticky="ew")

        self.clear_btn = tb.Button(button_grid, text="🗑️ 清空",
                            bootstyle=WARNING, width=10)
        self.clear_btn.grid(row=0, column=1, padx=6, pady=2, sticky="ew")

        self.capture_btn = tb.Button(button_grid, text="📷 截图翻译",
                            bootstyle=INFO, width=10)
        self.capture_btn.grid(row=0, column=2, padx=6, pady=2, sticky="ew")

        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)
        button_grid.columnconfigure(2, weight=1)

class ConfigTabManager:
    def __init__(self, notebook, settings_manager):
        self.notebook = notebook
        self.settings_manager = settings_manager
        self.theme_var = None
        self.appid_entry = None
        self.appkey_entry = None
        self.translate_shortcut = None
        self.clear_shortcut = None
        self.capture_shortcut = None
        
    def setup(self):
        """设置配置标签页"""
        config_frame = tb.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ 配置")

        main_container = tb.Frame(config_frame)
        main_container.pack(padx=20, pady=20, fill=BOTH, expand=True)
        main_container.columnconfigure(0, weight=1)

        left_panel = tb.Frame(main_container)
        left_panel.grid(row=0, column=0, sticky="nsew")

        right_panel = tb.Frame(main_container)
        right_panel.grid(row=0, column=1, sticky="ns", padx=(10, 0))

        self._create_theme_settings(left_panel)
        self._create_api_settings(left_panel)
        self._create_shortcut_settings(left_panel)
        self._create_save_button(right_panel)

    def _create_theme_settings(self, parent):
        """创建主题设置区域"""
        theme_frame = tb.LabelFrame(parent, text="界面主题", padding=10, bootstyle=INFO)
        theme_frame.pack(fill="x", padx=5, pady=5)
        theme_frame.columnconfigure(1, weight=1)

        tb.Label(theme_frame, text="选择主题:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = tb.StringVar()
        self.theme_combo = tb.Combobox(theme_frame, width=10, state="readonly",
                                    textvariable=self.theme_var, bootstyle=PRIMARY)
        self.theme_combo['values'] = ('白天', '黑夜')
        self.theme_combo.set('白天')
        self.theme_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")


    def _create_api_settings(self, parent):
        """创建API设置区域"""
        api_frame = tb.LabelFrame(parent, text="百度翻译API", padding=15, bootstyle=INFO)
        api_frame.pack(fill="x", padx=5, pady=5)
        api_frame.columnconfigure(1, weight=1)

        tb.Label(api_frame, text="APPID:", font=('微软雅黑', 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.appid_entry = tb.Entry(api_frame, bootstyle=PRIMARY, font=('微软雅黑', 10))
        self.appid_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(api_frame, text="APPKEY:", font=('微软雅黑', 10)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.appkey_entry = tb.Entry(api_frame, show="*", bootstyle=PRIMARY, font=('微软雅黑', 10))
        self.appkey_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    def _create_shortcut_settings(self, parent):
        """创建快捷键设置区域"""
        shortcuts_frame = tb.LabelFrame(parent, text="快捷键设置", padding=15, bootstyle=INFO)
        shortcuts_frame.pack(fill="x", padx=5, pady=5)
        shortcuts_frame.columnconfigure(1, weight=1)

        tb.Label(shortcuts_frame, text="翻译:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.translate_shortcut = tb.Entry(shortcuts_frame, bootstyle=PRIMARY)
        self.translate_shortcut.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(shortcuts_frame, text="清空:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.clear_shortcut = tb.Entry(shortcuts_frame, bootstyle=PRIMARY)
        self.clear_shortcut.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(shortcuts_frame, text="截图翻译:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.capture_shortcut = tb.Entry(shortcuts_frame, bootstyle=PRIMARY)
        self.capture_shortcut.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    def _create_save_button(self, parent):
        """创建保存按钮"""
        self.save_btn = tb.Button(parent, text="💾 保存配置", 
                                bootstyle=SUCCESS, width=15)
        self.save_btn.pack(pady=10)
    def load_shortcuts(self):
        """加载快捷键配置"""
        shortcuts = self.settings_manager.load_shortcuts()
        self.translate_shortcut.delete(0, "end")
        self.translate_shortcut.insert(0, shortcuts.get('translate', '<Control-Return>'))
        self.clear_shortcut.delete(0, "end")
        self.clear_shortcut.insert(0, shortcuts.get('clear', '<Control-d>'))
        self.capture_shortcut.delete(0, "end")
        self.capture_shortcut.insert(0, shortcuts.get('capture', '<Control-s>'))

class AboutTabManager:
    def __init__(self, notebook):
        self.notebook = notebook
        
    def setup(self):
        """设置关于标签页"""
        from version_config import VERSION_INFO
        
        about_frame = tb.Frame(self.notebook)
        self.notebook.add(about_frame, text="ℹ️ 关于")

        about_container = tb.Frame(about_frame)
        about_container.pack(padx=20, pady=20, fill=BOTH, expand=True)

        # 创建Logo和标题区域
        self._create_header(about_container, VERSION_INFO)
        # 创建信息卡片
        self._create_info_card(about_container, VERSION_INFO)
        # 创建功能说明
        self._create_features(about_container, VERSION_INFO)

    def _create_header(self, parent, version_info):
        """创建标题区域"""
        logo_frame = tb.Frame(parent)
        logo_frame.pack(fill=X, pady=(0, 20))
        
        title_label = tb.Label(logo_frame, text="翻译工具", 
                            font=('微软雅黑', 24, 'bold'))
        title_label.pack()
        
        version_label = tb.Label(logo_frame, text=f"Version {version_info['version']}", 
                            font=('微软雅黑', 12))
        version_label.pack()

    def _create_info_card(self, parent, version_info):
        """创建信息卡片"""
        info_card = tb.LabelFrame(parent, text="软件信息", padding=20, bootstyle=INFO)
        info_card.pack(fill=X, pady=10)

        # 作者信息
        author_frame = tb.Frame(info_card)
        author_frame.pack(fill=X, pady=5)
        
        tb.Label(author_frame, text="作者：", font=('微软雅黑', 10)).pack(side=LEFT)
        tb.Label(author_frame, text=version_info['author'], font=('微软雅黑', 10, 'bold')).pack(side=LEFT)

        # GitHub链接
        github_frame = tb.Frame(info_card)
        github_frame.pack(fill=X, pady=5)
        
        tb.Label(github_frame, text="项目地址：", font=('微软雅黑', 10)).pack(side=LEFT)
        github_link = tb.Label(github_frame, text=version_info['github'], 
                            font=('微软雅黑', 10, 'bold'), foreground='blue', cursor='hand2')
        github_link.pack(side=LEFT)
        github_link.bind("<Button-1>", lambda e: self._open_link(version_info['github']))

    def _create_features(self, parent, version_info):
        """创建功能说明"""
        feature_frame = tb.LabelFrame(parent, text="主要功能", padding=20, bootstyle=INFO)
        feature_frame.pack(fill=X, pady=10)

        for feature in version_info['features']:
            tb.Label(feature_frame, text=feature, font=('微软雅黑', 10)).pack(anchor=W, pady=2)

    def _open_link(self, url):
        """打开链接"""
        import webbrowser
        webbrowser.open(url)

class UIManager:
    def __init__(self, root, settings_manager):
        self.root = root
        self.settings_manager = settings_manager
        self._translate_lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        
        # 初始化管理器
        self.title_bar_manager = TitleBarManager(root)
        self.translate_tab_manager = None
        self.config_tab_manager = None
        self.about_tab_manager = None
        self.translator = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        try:
            # 基本窗口设置
            self.root.overrideredirect(True)
            self.root.style.configure('TNotebook', tabposition='nw')
            self.root.style.configure('TNotebook.Tab', padding=[20, 10])

            # 创建主要UI组件
            self.title_bar_manager.setup()
            
            main_container = tb.Frame(self.root)
            main_container.pack(padx=20, pady=20, fill=BOTH, expand=True)

            notebook = tb.Notebook(main_container, bootstyle=INFO)
            notebook.pack(fill=BOTH, expand=True)

            # 创建标签页管理器
            self.translate_tab_manager = TranslateTabManager(notebook, self.settings_manager)
            self.config_tab_manager = ConfigTabManager(notebook, self.settings_manager)
            self.about_tab_manager = AboutTabManager(notebook)

            # 设置各个标签页
            self.translate_tab_manager.setup()
            self.config_tab_manager.setup()
            self.about_tab_manager.setup()

            # 绑定事件
            self._bind_events()

            logging.info("界面初始化完成")
        except Exception as e:
            logging.error(f"界面初始化失败: {str(e)}")
            Messagebox.show_error("错误", f"界面初始化失败: {str(e)}")

    def _bind_events(self):
        """绑定事件"""
        # 绑定主题切换事件
        self.config_tab_manager.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        
        # 绑定按钮事件
        self.translate_tab_manager.translate_btn.configure(command=self.translate)
        self.translate_tab_manager.clear_btn.configure(command=self.clear_text)
        self.translate_tab_manager.capture_btn.configure(command=self.capture_translate)
        self.config_tab_manager.save_btn.configure(command=self.save_config)

        # 绑定快捷键
        self.bind_shortcuts()

    def on_theme_change(self, event=None):
        """处理主题切换"""
        theme = self.config_tab_manager.theme_var.get()
        self.settings_manager.set_theme(theme)
        self.title_bar_manager.update_style(theme)

    def bind_shortcuts(self):
        """绑定快捷键"""
        try:
            # 先解绑所有已存在的快捷键
            self.root.unbind_class('Toplevel', '<Control-Return>')
            self.root.unbind_class('Toplevel', '<Control-d>')
            self.root.unbind_class('Toplevel', '<Control-s>')
            
            # 加载快捷键配置
            shortcuts = self.settings_manager.load_shortcuts()
            
            # 绑定新的快捷键
            self.root.bind(shortcuts.get('translate', '<Control-Return>'), lambda e: self.translate())
            self.root.bind(shortcuts.get('clear', '<Control-d>'), lambda e: self.clear_text())
            self.root.bind(shortcuts.get('capture', '<Control-s>'), lambda e: self.capture_translate())
            
            logging.info("快捷键绑定完成")
        except Exception as e:
            logging.error(f"绑定快捷键失败: {str(e)}")
            Messagebox.show_error("错误", f"绑定快捷键失败: {str(e)}")

    def save_config(self):
        """保存配置"""
        try:
            # 保存API配置
            appid = self.config_tab_manager.appid_entry.get().strip()
            appkey = self.config_tab_manager.appkey_entry.get().strip()
            
            # 保存快捷键配置
            shortcuts = {
                'translate': self.config_tab_manager.translate_shortcut.get(),
                'clear': self.config_tab_manager.clear_shortcut.get(),
                'capture': self.config_tab_manager.capture_shortcut.get()
            }
            
            # 保存主题配置
            theme = self.config_tab_manager.theme_var.get()
            
            # 保存语言配置
            source_lang = self.translate_tab_manager.source_lang.get()
            target_lang = self.translate_tab_manager.target_lang.get()

            # 保存所有配置
            if self.settings_manager.save_all_config(appid, appkey, shortcuts, theme, source_lang, target_lang):
                self.translator = BaiduTranslator(appid, appkey)
                Messagebox.show_info("成功", "配置已保存")
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
            Messagebox.show_error("错误", f"保存配置失败: {str(e)}")

    def load_config(self):
        """加载配置"""
        try:
            # 加载API配置
            appid, appkey = self.settings_manager.load_config()
            if appid and appkey:
                self.config_tab_manager.appid_entry.delete(0, "end")
                self.config_tab_manager.appid_entry.insert(0, appid)
                self.config_tab_manager.appkey_entry.delete(0, "end")
                self.config_tab_manager.appkey_entry.insert(0, appkey)
                self.translator = BaiduTranslator(appid, appkey)
            
            # 加载快捷键配置
            self.config_tab_manager.load_shortcuts()
            
            # 加载主题配置
            theme = self.settings_manager.load_theme()
            self.config_tab_manager.theme_var.set(theme)
            self.settings_manager.set_theme(theme)
            
            # 加载语言配置
            source_lang, target_lang = self.settings_manager.load_languages()
            self.translate_tab_manager.source_lang.set(source_lang)
            self.translate_tab_manager.target_lang.set(target_lang)

            logging.info("配置加载成功")
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
            Messagebox.show_error("错误", f"加载配置失败: {str(e)}")

    def translate(self):
        """执行翻译操作"""
        try:
            if not hasattr(self, 'translator') or not self.translator:
                Messagebox.show_error("错误", "请先保存配置")
                return
                
            source_text = self.translate_tab_manager.source_text.get("1.0", "end").strip()
            if not source_text:
                Messagebox.show_warning("警告", "请输入要翻译的文本")
                return
            
            if self._translate_lock.locked():
                Messagebox.show_warning("提示", "正在翻译中，请稍候...")
                return
            
            self._set_controls_state('disabled')
            self.thread_pool.submit(self._translate_thread, source_text)
            
        except Exception as e:
            logging.error(f"翻译操作失败: {str(e)}")
            Messagebox.show_error("错误", f"翻译失败: {str(e)}")
            self._set_controls_state('normal')

    def _translate_thread(self, source_text):
        """翻译线程"""
        try:
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
            
            from_lang = lang_map[self.translate_tab_manager.source_lang.get()]
            to_lang = lang_map[self.translate_tab_manager.target_lang.get()]
            
            result = self.translator.translate(source_text, from_lang=from_lang, to_lang=to_lang)
            
            self.root.after(0, self._update_result, result)
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            logging.error(error_msg)
            self.root.after(0, self._show_error, error_msg)
        finally:
            self.root.after(0, self._set_controls_state, 'normal')

    def _update_result(self, result):
        """更新翻译结果"""
        try:
            self.translate_tab_manager.target_text.text.configure(state='normal')
            self.translate_tab_manager.target_text.text.delete("1.0", "end")
            self.translate_tab_manager.target_text.text.insert("1.0", result)
            self.translate_tab_manager.target_text.text.configure(state='disabled')
            logging.info("翻译操作完成")
        except Exception as e:
            logging.error(f"更新翻译结果失败: {str(e)}")
        finally:
            self._set_controls_state('normal')

    def _show_error(self, error_msg):
        """显示错误信息"""
        try:
            Messagebox.show_error("错误", error_msg)
        except Exception as e:
            logging.error(f"显示错误信息失败: {str(e)}")
        finally:
            self._set_controls_state('normal')

    def _set_controls_state(self, state):
        """设置控件状态"""
        try:
            if state == 'normal':
                self.translate_tab_manager.translate_btn.configure(state='normal')
                self.translate_tab_manager.source_lang.configure(state='readonly')
                self.translate_tab_manager.target_lang.configure(state='readonly')
                self.translate_tab_manager.source_text.text.configure(state='normal')
            else:
                self.translate_tab_manager.translate_btn.configure(state='disabled')
                self.translate_tab_manager.source_lang.configure(state='disabled')
                self.translate_tab_manager.target_lang.configure(state='disabled')
                self.translate_tab_manager.source_text.text.configure(state='disabled')
        except Exception as e:
            logging.error(f"设置控件状态失败: {str(e)}")

    def clear_text(self):
        """清空文本框"""
        try:
            self.translate_tab_manager.source_text.text.configure(state='normal')
            self.translate_tab_manager.target_text.text.configure(state='normal')
            self.translate_tab_manager.source_text.text.delete("1.0", "end")
            self.translate_tab_manager.target_text.text.delete("1.0", "end")
            self.translate_tab_manager.target_text.text.configure(state='disabled')
            logging.info("清空文本框")
        except Exception as e:
            logging.error(f"清空文本框失败: {str(e)}")
            Messagebox.show_error("错误", f"清空文本框失败: {str(e)}")

    def capture_translate(self):
        """截图翻译"""
        try:
            if not hasattr(self, 'translator') or not self.translator:
                Messagebox.show_error("错误", "请先保存配置")
                return
            self._minimize_and_capture()
        except Exception as e:
            logging.error(f"截图翻译失败: {str(e)}")
            Messagebox.showerror("错误", f"截图翻译失败: {str(e)}")
            self.root.deiconify()

    def _minimize_and_capture(self):
        """最小化窗口并执行截图"""
        import pyautogui
        self.root.iconify()
        time.sleep(0.5)
        screenshot = pyautogui.screenshot()
        self._create_selection_window(screenshot)

    def _create_selection_window(self, screenshot):
        """创建选择窗口"""
        import tkinter as tk
        from PIL import Image, ImageTk
        
        selector = tk.Toplevel()
        selector.attributes('-fullscreen', True)
        selector.attributes('-alpha', 0.3)
        selector.configure(background='black')
        
        # 设置窗口始终在最前
        selector.attributes('-topmost', True)
        
        canvas = tk.Canvas(selector, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # 调整截图大小以适应屏幕
        screen_width = selector.winfo_screenwidth()
        screen_height = selector.winfo_screenheight()
        screenshot = screenshot.resize((screen_width, screen_height))
        
        photo = ImageTk.PhotoImage(screenshot)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.image = photo
        
        self._setup_selection_events(canvas, selector, screenshot)
        self._add_selection_hints(selector)
        selector.wait_window()

    def _setup_selection_events(self, canvas, selector, screenshot):
        """设置选择事件"""
        start_x = start_y = None
        
        def on_mouse_down(event):
            nonlocal start_x, start_y
            start_x = event.x
            start_y = event.y
            self._create_selection_rect(canvas, start_x, start_y, start_x, start_y)
            
        def on_mouse_drag(event):
            if start_x is not None and start_y is not None:
                self._update_selection_rect(canvas, start_x, start_y, event.x, event.y)
                
        def on_mouse_up(event):
            if start_x is not None and start_y is not None:
                self._process_selection(canvas, selector, screenshot, start_x, start_y, event.x, event.y)
        
        canvas.bind('<Button-1>', on_mouse_down)
        canvas.bind('<B1-Motion>', on_mouse_drag)
        canvas.bind('<ButtonRelease-1>', on_mouse_up)
        selector.bind('<Escape>', lambda e: self._cancel_selection(selector))

    def _create_selection_rect(self, canvas, x1, y1, x2, y2):
        """创建选择框"""
        # 创建外边框
        canvas.create_rectangle(x1-1, y1-1, x2+1, y2+1, outline='white', width=1, tags='selection')
        # 创建主边框
        canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2, tags='selection')
        # 创建半透明填充
        canvas.create_rectangle(x1, y1, x2, y2, fill='white', stipple='gray25', tags='selection')

    def _update_selection_rect(self, canvas, x1, y1, x2, y2):
        """更新选择框"""
        canvas.delete('selection')
        self._create_selection_rect(canvas, x1, y1, x2, y2)

    def _process_selection(self, canvas, selector, screenshot, x1, y1, x2, y2):
        """处理选择区域"""
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        if width < 10 or height < 10:  # 增加最小选择区域
            selector.destroy()
            self.root.deiconify()
            return
        
        # 添加选择确认动画
        canvas.create_rectangle(x, y, x+width, y+height, outline='green', width=3, tags='confirm')
        selector.update()
        time.sleep(0.2)  # 短暂延迟以显示确认效果
        
        selected_area = screenshot.crop((x, y, x + width, y + height))
        temp_image = os.path.join('data', 'temp_screenshot.png')
        selected_area.save(temp_image)
        
        selector.destroy()
        self._process_ocr_result(temp_image)

    def _process_ocr_result(self, temp_image):
        """处理OCR识别结果"""
        import pytesseract
        from PIL import Image
        
        self.root.deiconify()
        
        try:
            text = pytesseract.image_to_string(Image.open(temp_image), lang='chi_sim+eng')
            
            if text.strip():
                self.translate_tab_manager.source_text.text.configure(state='normal')
                self.translate_tab_manager.source_text.text.delete("1.0", "end")
                self.translate_tab_manager.source_text.text.insert("1.0", text.strip())
                self.translate_tab_manager.source_text.text.configure(state='disabled')
                self.translate()
            else:
                Messagebox.show_warning("提示", "未能识别到文本")
        finally:
            try:
                os.remove(temp_image)
            except:
                pass

    def _add_selection_hints(self, selector):
        """添加选择提示"""
        import tkinter as tk
        hint_frame = tk.Frame(selector, bg='black')
        hint_frame.place(relx=0.5, rely=0.1, anchor='center')
        
        tk.Label(
            hint_frame,
            text="按住鼠标左键并拖动来选择要翻译的区域",
            bg='black',
            fg='white',
            font=('微软雅黑', 12)
        ).pack()
        
        tk.Label(
            hint_frame,
            text="按 ESC 键取消",
            bg='black',
            fg='gray',
            font=('微软雅黑', 10)
        ).pack()

    def _cancel_selection(self, selector):
        """取消选择"""
        selector.destroy()
        self.root.deiconify()
