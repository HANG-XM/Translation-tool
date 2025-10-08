# 翻译工具

一个基于Python的桌面翻译应用，支持文本翻译和截图翻译功能，使用百度翻译API。

## 功能特点

- 📸 **截图翻译**：支持截取屏幕区域进行OCR识别并翻译
- 🔤 **多语言支持**：支持中文、英语、日语、韩语、法语、德语、俄语、西班牙语互译
- 🎨 **主题切换**：支持白天/黑夜两种主题模式
- ⌨️ **快捷键操作**：可自定义快捷键提升使用效率
- 💾 **配置持久化**：自动保存API配置、语言设置和主题偏好

## 相关技术

- Python：核心开发语言
- tkinter：GUI框架
- ttkbootstrap：UI主题框架
- pytesseract：OCR文字识别
- PIL：图像处理
- pyautogui：屏幕操作
- threading：多线程处理
- hashlib：加密签名
- requests：HTTP请求
- configparser：配置文件处理

## 系统要求

- Windows 10/11
- Python 3.13+
- Tesseract-OCR（用于OCR功能）

## 安装说明

1. 安装Tesseract-OCR
下载地址：https://github.com/UB-Mannheim/tesseract/wiki
2. 配置百度翻译API

## 目录结构

```text
translator/
├── main.py              # 主程序入口
├── translator.py        # 翻译核心功能
├── settings_manager.py  # 设置管理
├── ui_manager.py        # 界面管理
├── data/               # 数据目录
│   └── config.ini      # 配置文件
├── log/                # 日志目录
├── requirements.txt    # 依赖列表
└── README.md          # 说明文档