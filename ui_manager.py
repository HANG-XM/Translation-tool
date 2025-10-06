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
            main_container = tb.Frame(self.root)
            main_container.pack(padx=15, pady=15, fill=BOTH, expand=True)

            config_frame = tb.LabelFrame(main_container, text="配置", padding=15, bootstyle=INFO)
            config_frame.pack(fill=X, pady=(0, 15))
            
            config_grid = tb.Frame(config_frame)
            config_grid.pack(fill=X)
            
            tb.Label(config_grid, text="主题:").grid(row=0, column=0, padx=8, sticky=W)
            self.theme_var = tb.StringVar()
            self.theme_combo = tb.Combobox(config_grid, width=12, state="readonly",
                                        textvariable=self.theme_var, bootstyle=PRIMARY)
            self.theme_combo['values'] = ('白天', '黑夜')
            self.theme_combo.set('白天')
            self.theme_combo.grid(row=0, column=1, padx=8)
            self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
            
            tb.Label(config_grid, text="APPID:").grid(row=0, column=2, padx=(25, 8), sticky=W)
            self.appid_entry = tb.Entry(config_grid, width=35)
            self.appid_entry.grid(row=0, column=3, padx=8)
            
            tb.Label(config_grid, text="APPKEY:").grid(row=0, column=4, padx=(25, 8), sticky=W)
            self.appkey_entry = tb.Entry(config_grid, width=35, show="*")
            self.appkey_entry.grid(row=0, column=5, padx=8)
            
            save_btn = tb.Button(config_grid, text="保存配置", command=self.save_config, 
                            bootstyle=SUCCESS, width=15)
            save_btn.grid(row=0, column=6, padx=(25, 0))

            lang_frame = tb.LabelFrame(main_container, text="语言设置", padding=15, bootstyle=INFO)
            lang_frame.pack(fill=X, pady=(0, 15))
            
            lang_grid = tb.Frame(lang_frame)
            lang_grid.pack(fill=X)
            
            tb.Label(lang_grid, text="源语言:").grid(row=0, column=0, padx=8, sticky=W)
            self.source_lang = tb.Combobox(lang_grid, width=18, state="readonly", bootstyle=INFO)
            self.source_lang['values'] = ('自动检测', '中文', '英语', '日语', '韩语', '法语', '德语', '俄语', '西班牙语')
            self.source_lang.set('自动检测')
            self.source_lang.grid(row=0, column=1, padx=8)
            
            tb.Label(lang_grid, text="目标语言:").grid(row=0, column=2, padx=(25, 8), sticky=W)
            self.target_lang = tb.Combobox(lang_grid, width=18, state="readonly", bootstyle=INFO)
            self.target_lang['values'] = ('中文', '英语', '日语', '韩语', '法语', '德语', '俄语', '西班牙语')
            self.target_lang.set('英语')
            self.target_lang.grid(row=0, column=3, padx=8)

            text_container = tb.Frame(main_container)
            text_container.pack(fill=BOTH, expand=True)

            paned_window = tb.PanedWindow(text_container, orient=VERTICAL)
            paned_window.pack(fill=BOTH, expand=True)

            source_frame = tb.LabelFrame(paned_window, text="源文本", padding=10, bootstyle=PRIMARY)
            paned_window.add(source_frame, weight=1)

            self.source_text = ScrolledText(source_frame, wrap="word", height=8,
                                        font=('微软雅黑', 12))
            self.source_text.pack(padx=10, pady=10, fill=BOTH, expand=True)

            button_frame = tb.Frame(paned_window)
            button_frame.pack(fill=X, pady=5)
            paned_window.add(button_frame, weight=0)

            button_container = tb.Frame(button_frame)
            button_container.pack()

            self.translate_btn = tb.Button(button_container, text="翻译", command=self.translate, 
                                        bootstyle=PRIMARY, width=18)
            self.translate_btn.pack(side=LEFT, padx=10)

            clear_btn = tb.Button(button_container, text="清空", command=self.clear_text, 
                                bootstyle=WARNING, width=18)
            clear_btn.pack(side=LEFT, padx=10)

            capture_btn = tb.Button(button_container, text="截图翻译", command=self.capture_translate, 
                                  bootstyle=INFO, width=18)
            capture_btn.pack(side=LEFT, padx=10)

            target_frame = tb.LabelFrame(paned_window, text="翻译结果", padding=10, bootstyle=PRIMARY)
            paned_window.add(target_frame, weight=2)

            self.target_text = ScrolledText(target_frame, wrap="word", height=12, 
                                        font=('微软雅黑', 12))
            self.target_text.pack(padx=10, pady=10, fill=BOTH, expand=True)
            
            config_grid.columnconfigure(3, weight=1)
            config_grid.columnconfigure(5, weight=1)
            
            logging.info("界面初始化完成")
        except Exception as e:
            logging.error(f"界面初始化失败: {str(e)}")
            Messagebox.showerror("错误", f"界面初始化失败: {str(e)}")

    def on_theme_change(self, event=None):
        """主题切换事件"""
        theme = self.theme_var.get()
        self.settings_manager.set_theme(theme)
    
    def save_config(self):
        """保存配置"""
        appid = self.appid_entry.get().strip()
        appkey = self.appkey_entry.get().strip()
        
        if self.settings_manager.save_config(appid, appkey):
            self.translator = BaiduTranslator(appid, appkey)
            Messagebox.show_info("成功", "配置已保存")
    
    def load_config(self):
        """加载配置"""
        appid, appkey = self.settings_manager.load_config()
        
        if appid and appkey:
            self.appid_entry.delete(0, "end")
            self.appid_entry.insert(0, appid)
            
            self.appkey_entry.delete(0, "end")
            self.appkey_entry.insert(0, appkey)
            
            self.translator = BaiduTranslator(appid, appkey)
            logging.info("配置加载成功")

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
        selector.attributes('-alpha', 0.4)
        selector.configure(background='black')
        
        canvas = tk.Canvas(selector, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
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
        canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2, tags='selection')
        canvas.create_rectangle(x1, y1, x2, y2, fill='white', stipple='gray50', tags='selection')

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
        
        if width < 5 or height < 5:
            selector.destroy()
            self.root.deiconify()
            return
        
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
