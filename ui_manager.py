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

class UIManager:
    def __init__(self, root, settings_manager):
        self.root = root
        self.settings_manager = settings_manager
        self._translate_lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        try:
            # 设置窗口样式
            self.root.style.configure('TNotebook', tabposition='nw')
            self.root.style.configure('TNotebook.Tab', padding=[20, 10])
            
            main_container = tb.Frame(self.root)
            main_container.pack(padx=20, pady=20, fill=BOTH, expand=True)

            # 创建Notebook
            self.notebook = tb.Notebook(main_container, bootstyle=INFO)
            self.notebook.pack(fill=BOTH, expand=True)

            # 第一个标签页：截图翻译
            self.setup_translate_tab()

            # 第二个标签页：配置
            self.setup_config_tab()

            # 第三个标签页：关于
            self.setup_about_tab()

            logging.info("界面初始化完成")
        except Exception as e:
            logging.error(f"界面初始化失败: {str(e)}")
            Messagebox.show_error("错误", f"界面初始化失败: {str(e)}")

    def setup_translate_tab(self):
        """设置截图翻译标签页"""
        translate_frame = tb.Frame(self.notebook)
        self.notebook.add(translate_frame, text="📸 截图翻译")

        # 用 grid 进行整体布局
        translate_frame.rowconfigure(1, weight=1)  # 文本区可扩展
        translate_frame.columnconfigure(0, weight=1)

        # 顶部工具栏
        toolbar = tb.Frame(translate_frame, bootstyle=SECONDARY)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # 语言选择区域
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

        # 文本区域
        text_container = tb.Frame(translate_frame)
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

        # 底部工具栏
        bottom_toolbar = tb.Frame(translate_frame, bootstyle=SECONDARY)
        bottom_toolbar.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))

        # 按钮区域
        button_frame = tb.LabelFrame(bottom_toolbar, text="操作", padding=6, bootstyle=INFO)
        button_frame.pack(side=TOP, padx=0, pady=0, fill=X)

        button_grid = tb.Frame(button_frame)
        button_grid.pack(fill=X)

        self.translate_btn = tb.Button(button_grid, text="🔤 翻译", command=self.translate,
                                    bootstyle=PRIMARY, width=10)
        self.translate_btn.grid(row=0, column=0, padx=6, pady=2, sticky="ew")
        self._create_tooltip(self.translate_btn, "翻译输入的文本 (Ctrl+Enter)")

        self.clear_btn = tb.Button(button_grid, text="🗑️ 清空", command=self.clear_text,
                            bootstyle=WARNING, width=10)
        self.clear_btn.grid(row=0, column=1, padx=6, pady=2, sticky="ew")
        self._create_tooltip(self.clear_btn, "清空所有文本 (Ctrl+D)")

        self.capture_btn = tb.Button(button_grid, text="📷 截图翻译", command=self.capture_translate,
                            bootstyle=INFO, width=10)
        self.capture_btn.grid(row=0, column=2, padx=6, pady=2, sticky="ew")
        self._create_tooltip(self.capture_btn, "截取屏幕上的文本进行翻译 (Ctrl+S)")

        button_grid.columnconfigure(0, weight=1)
        button_grid.columnconfigure(1, weight=1)
        button_grid.columnconfigure(2, weight=1)
    def _create_tooltip(self, widget, text):
        """创建工具提示"""
        def on_enter(event):
            tooltip = tb.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tb.Label(tooltip, text=text, bootstyle=INFO)
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def setup_config_tab(self):
        """设置配置标签页"""
        config_frame = tb.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ 配置")

        # 创建主容器
        main_container = tb.Frame(config_frame)
        main_container.pack(padx=20, pady=20, fill=BOTH, expand=True)
        main_container.columnconfigure(0, weight=1)

        # 创建左右分栏
        left_panel = tb.Frame(main_container)
        left_panel.grid(row=0, column=0, sticky="nsew")

        right_panel = tb.Frame(main_container)
        right_panel.grid(row=0, column=1, sticky="ns", padx=(10, 0))

        # 主题设置
        theme_frame = tb.LabelFrame(left_panel, text="界面主题", padding=10, bootstyle=INFO)
        theme_frame.pack(fill="x", padx=5, pady=5)
        theme_frame.columnconfigure(1, weight=1)

        tb.Label(theme_frame, text="选择主题:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = tb.StringVar()
        self.theme_combo = tb.Combobox(theme_frame, width=10, state="readonly",
                                    textvariable=self.theme_var, bootstyle=PRIMARY)
        self.theme_combo['values'] = ('白天', '黑夜')
        self.theme_combo.set('白天')
        self.theme_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)

        # API设置
        api_frame = tb.LabelFrame(left_panel, text="百度翻译API", padding=15, bootstyle=INFO)
        api_frame.pack(fill="x", padx=5, pady=5)
        api_frame.columnconfigure(1, weight=1)

        tb.Label(api_frame, text="APPID:", font=('微软雅黑', 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.appid_entry = tb.Entry(api_frame, bootstyle=PRIMARY, font=('微软雅黑', 10))
        self.appid_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(api_frame, text="APPKEY:", font=('微软雅黑', 10)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.appkey_entry = tb.Entry(api_frame, show="*", bootstyle=PRIMARY, font=('微软雅黑', 10))
        self.appkey_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # 快捷键设置
        shortcuts_frame = tb.LabelFrame(left_panel, text="快捷键设置", padding=15, bootstyle=INFO)
        shortcuts_frame.pack(fill="x", padx=5, pady=5)
        shortcuts_frame.columnconfigure(1, weight=1)

        # 翻译快捷键
        tb.Label(shortcuts_frame, text="翻译:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.translate_shortcut = tb.Entry(shortcuts_frame, bootstyle=PRIMARY)
        self.translate_shortcut.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 清空快捷键
        tb.Label(shortcuts_frame, text="清空:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.clear_shortcut = tb.Entry(shortcuts_frame, bootstyle=PRIMARY)
        self.clear_shortcut.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # 截图快捷键
        tb.Label(shortcuts_frame, text="截图翻译:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.capture_shortcut = tb.Entry(shortcuts_frame, bootstyle=PRIMARY)
        self.capture_shortcut.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # 加载已保存的快捷键配置
        shortcuts = self.settings_manager.load_shortcuts()
        self.translate_shortcut.insert(0, shortcuts.get('translate', '<Control-Return>'))
        self.clear_shortcut.insert(0, shortcuts.get('clear', '<Control-d>'))
        self.capture_shortcut.insert(0, shortcuts.get('capture', '<Control-s>'))

        # 保存按钮移到右侧
        save_btn = tb.Button(right_panel, text="💾 保存配置", command=self.save_config, 
                            bootstyle=SUCCESS, width=15)
        save_btn.pack(pady=10)
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

    def setup_about_tab(self):
        """设置关于标签页"""
        from version_config import VERSION_INFO
        
        about_frame = tb.Frame(self.notebook)
        self.notebook.add(about_frame, text="ℹ️ 关于")

        about_container = tb.Frame(about_frame)
        about_container.pack(padx=20, pady=20, fill=BOTH, expand=True)

        # Logo和标题
        logo_frame = tb.Frame(about_container)
        logo_frame.pack(fill=X, pady=(0, 20))
        
        title_label = tb.Label(logo_frame, text="翻译工具", 
                            font=('微软雅黑', 24, 'bold'))
        title_label.pack()
        
        version_label = tb.Label(logo_frame, text=f"Version {VERSION_INFO['version']}", 
                            font=('微软雅黑', 12))
        version_label.pack()

        # 信息卡片
        info_card = tb.LabelFrame(about_container, text="软件信息", padding=20, bootstyle=INFO)
        info_card.pack(fill=X, pady=10)

        # 作者信息
        author_frame = tb.Frame(info_card)
        author_frame.pack(fill=X, pady=5)
        
        tb.Label(author_frame, text="作者：", font=('微软雅黑', 10)).pack(side=LEFT)
        tb.Label(author_frame, text=VERSION_INFO['author'], font=('微软雅黑', 10, 'bold')).pack(side=LEFT)

        # GitHub链接
        github_frame = tb.Frame(info_card)
        github_frame.pack(fill=X, pady=5)
        
        tb.Label(github_frame, text="项目地址：", font=('微软雅黑', 10)).pack(side=LEFT)
        github_link = tb.Label(github_frame, text=VERSION_INFO['github'], 
                            font=('微软雅黑', 10, 'bold'), foreground='blue', cursor='hand2')
        github_link.pack(side=LEFT)
        github_link.bind("<Button-1>", lambda e: self._open_link(VERSION_INFO['github']))

        # 功能说明
        feature_frame = tb.LabelFrame(about_container, text="主要功能", padding=20, bootstyle=INFO)
        feature_frame.pack(fill=X, pady=10)

        for feature in VERSION_INFO['features']:
            tb.Label(feature_frame, text=feature, font=('微软雅黑', 10)).pack(anchor=W, pady=2)

    def _open_link(self, url):
        """打开链接"""
        import webbrowser
        webbrowser.open(url)

    def on_theme_change(self, event=None):
        """主题切换事件"""
        theme = self.theme_var.get()
        self.settings_manager.set_theme(theme)
    
    def save_config(self):
        """保存配置"""
        try:
            # 保存API配置
            appid = self.appid_entry.get().strip()
            appkey = self.appkey_entry.get().strip()
            
            # 保存快捷键配置
            shortcuts = {
                'translate': self.translate_shortcut.get(),
                'clear': self.clear_shortcut.get(),
                'capture': self.capture_shortcut.get()
            }
            
            # 保存主题配置
            theme = self.theme_var.get()
            
            # 保存语言配置
            source_lang = self.source_lang.get()
            target_lang = self.target_lang.get()

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
                self.appid_entry.delete(0, "end")
                self.appid_entry.insert(0, appid)
                self.appkey_entry.delete(0, "end")
                self.appkey_entry.insert(0, appkey)
                self.translator = BaiduTranslator(appid, appkey)
            
            # 加载快捷键配置
            shortcuts = self.settings_manager.load_shortcuts()
            self.translate_shortcut.delete(0, "end")
            self.translate_shortcut.insert(0, shortcuts.get('translate', '<Control-Return>'))
            self.clear_shortcut.delete(0, "end")
            self.clear_shortcut.insert(0, shortcuts.get('clear', '<Control-d>'))
            self.capture_shortcut.delete(0, "end")
            self.capture_shortcut.insert(0, shortcuts.get('capture', '<Control-s>'))
            
            # 加载主题配置
            theme = self.settings_manager.load_theme()
            self.theme_var.set(theme)
            self.settings_manager.set_theme(theme)
            
            # 加载语言配置
            source_lang, target_lang = self.settings_manager.load_languages()
            self.source_lang.set(source_lang)
            self.target_lang.set(target_lang)

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
                
            source_text = self.source_text.get("1.0", "end").strip()
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
            
            from_lang = lang_map[self.source_lang.get()]
            to_lang = lang_map[self.target_lang.get()]
            
            result = self.translator.translate(source_text, from_lang=from_lang, to_lang=to_lang)
            
            self.root.after(0, self._update_result, result)
        except Exception as e:
            error_msg = f"翻译失败: {str(e)}"
            logging.error(error_msg)
            self.root.after(0, self._show_error, error_msg)
        finally:
            self.root.after(0, self._set_controls_state, 'normal')

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
        size_label = None
        
        def on_mouse_down(event):
            nonlocal start_x, start_y
            start_x = event.x
            start_y = event.y
            self._create_selection_rect(canvas, start_x, start_y, start_x, start_y)
            
        def on_mouse_drag(event):
            if start_x is not None and start_y is not None:
                self._update_selection_rect(canvas, start_x, start_y, event.x, event.y, size_label)
                
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

    def _update_selection_rect(self, canvas, x1, y1, x2, y2, size_label):
        """更新选择框"""
        canvas.delete('selection')
        self._create_selection_rect(canvas, x1, y1, x2, y2)
        
        if size_label:
            canvas.delete(size_label)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        size_label = canvas.create_text(
            x2, y2 - 20,
            text=f"{width} × {height}",
            fill='white',
            font=('微软雅黑', 10),
            anchor=tk.S,
            tags='selection'
        )

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
                self.source_text.text.delete("1.0", "end")
                self.source_text.text.insert("1.0", text.strip())
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

    def _update_result(self, result):
        """更新翻译结果"""
        try:
            self.target_text.text.configure(state='normal')
            self.target_text.text.delete("1.0", "end")
            self.target_text.text.insert("1.0", result)
            self.target_text.text.configure(state='disabled')
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
                self.translate_btn.configure(state='normal')
                self.source_lang.configure(state='readonly')
                self.target_lang.configure(state='readonly')
                self.source_text.text.configure(state='normal')
            else:
                self.translate_btn.configure(state='disabled')
                self.source_lang.configure(state='disabled')
                self.target_lang.configure(state='disabled')
                self.source_text.text.configure(state='disabled')
        except Exception as e:
            logging.error(f"设置控件状态失败: {str(e)}")

    def clear_text(self):
        """清空文本框"""
        try:
            self.source_text.text.configure(state='normal')
            self.target_text.text.configure(state='normal')
            self.source_text.text.delete("1.0", "end")
            self.target_text.text.delete("1.0", "end")
            self.target_text.text.configure(state='disabled')
            logging.info("清空文本框")
        except Exception as e:
            logging.error(f"清空文本框失败: {str(e)}")
            Messagebox.show_error("错误", f"清空文本框失败: {str(e)}")
