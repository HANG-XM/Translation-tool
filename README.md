# 翻译工具

一个基于Python的桌面翻译应用，支持文本翻译和截图翻译功能，使用百度翻译API。

## 功能特点

- 📸 **截图翻译**：支持截取屏幕区域进行OCR识别并翻译
- 🔤 **多语言支持**：支持中文、英语、日语、韩语、法语、德语、俄语、西班牙语互译
- 🎨 **主题切换**：支持白天/黑夜两种主题模式
- ⌨️ **快捷键操作**：可自定义快捷键提升使用效率
- 💾 **配置持久化**：自动保存API配置、语言设置和主题偏好

## 相关技术
- **核心框架**：
  - Python 3.13+：核心开发语言
  - ttkbootstrap：现代化的 UI 主题框架，提供美观的界面组件
  - tkinter：基础 GUI 框架

- **翻译相关**：
  - requests：HTTP 请求处理，用于调用百度翻译 API
  - hashlib：MD5 加密，用于生成 API 签名
  - urllib3：请求重试机制，提高翻译请求的稳定性

- **图像处理**：
  - PIL (Pillow)：图像处理和截图功能
  - pyautogui：屏幕截图和窗口操作
  - pytesseract：OCR 文字识别，支持中英文识别

- **数据处理**：
  - configparser：配置文件管理
  - json：历史记录数据存储
  - collections.OrderedDict：翻译缓存管理

- **并发处理**：
  - threading：多线程处理，避免界面卡顿
  - concurrent.futures：线程池管理
  - queue：任务队列管理

- **日志系统**：
  - logging：日志记录
  - logging.handlers.RotatingFileHandler：日志轮转管理

- **打包工具**：
  - pyinstaller：程序打包，生成独立可执行文件

## 系统要求

- Windows 10/11
- Python 3.13+
- Tesseract-OCR（用于OCR功能）

## 安装说明

1. 安装Tesseract-OCR
下载地址：https://github.com/UB-Mannheim/tesseract/wiki
2. 配置百度翻译API
在「配置」标签页中填入您的百度翻译 API 的 APP ID 和 密钥。
## 目录结构

```text
translator/
├── src/                 # 源代码目录
│   ├── main.py         # 主程序入口
│   ├── translator.py   # 翻译核心功能
│   ├── settings_manager.py  # 设置管理
│   ├── ui_manager.py   # 界面管理
│   └── version_config.py # 版本配置
├── resources/          # 资源目录（图标等）
├── data/               # 数据目录（自动创建）
├── log/                # 日志目录（自动创建）
├── build.py            # 构建脚本
├── requirements.txt    # 依赖列表
└── README.md           # 说明文档