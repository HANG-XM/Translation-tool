# 翻译工具

一个基于Python开发的桌面翻译工具，支持文本翻译和截图翻译功能。

## 功能特点

- 📝 文本翻译：支持多语言互译
- 📸 截图翻译：支持屏幕截图OCR识别翻译
- 🎨 主题切换：支持白天/黑夜主题
- 💾 配置管理：支持百度翻译API配置保存
- 🚀 高效缓存：内置翻译结果缓存机制
- 🌍 多语言支持：支持中文、英语、日语、韩语、法语、德语、俄语、西班牙语

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