
# 翻译工具

一个功能强大的桌面翻译应用，支持文本翻译、截图翻译和语音朗读，使用百度翻译API提供多语言翻译服务。

## 🌟 主要功能

- **📸 截图翻译**：支持屏幕区域截图，自动OCR识别并翻译
- **🔤 文本翻译**：支持中英日韩法德俄西等多种语言互译
- **🎨 主题切换**：提供白天/黑夜两种主题模式
- **⌨️ 快捷键操作**：可自定义快捷键提升使用效率
- **📜 历史记录**：自动保存翻译历史，支持搜索和查看详情
- **🔊 语音朗读**：支持翻译结果的语音朗读功能
- **📄 多格式导出**：支持导出为TXT、Word、PDF、JSON格式
- **📊 翻译统计**：记录翻译次数和字符数统计

## 🛠️ 技术栈

- **核心框架**：Python 3.13+、ttkbootstrap、tkinter
- **翻译服务**：百度翻译API
- **图像处理**：PIL(Pillow)、pyautogui、pytesseract
- **数据处理**：configparser、json、collections.OrderedDict
- **并发处理**：threading、concurrent.futures
- **日志系统**：logging、RotatingFileHandler
- **打包工具**：pyinstaller

## 📋 系统要求

- Windows 10/11
- Python 3.13+
- Tesseract-OCR（用于OCR功能）
- 百度翻译API账号

## 🚀 快速开始

### 环境准备

1. **安装Python 3.13+**
   ```bash
   # 从官网下载并安装Python 3.13+
   # 确保勾选"Add Python to PATH"
   ```

2. **安装Tesseract-OCR**
   - 下载地址：[https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - 安装后记住安装路径（默认：`C:\Program Files\Tesseract-OCR`）

3. **克隆项目**
   ```bash
   git clone <项目地址>
   cd translator
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

### 运行程序

1. **配置百度翻译API**
   - 在百度翻译开放平台注册账号：[https://fanyi-api.baidu.com/](https://fanyi-api.baidu.com/)
   - 创建应用获取APP ID和密钥

2. **启动程序**
   ```bash
   python src/main.py
   ```

3. **首次使用**
   - 在"配置"标签页中填入百度翻译API的APP ID和密钥
   - 点击"保存配置"完成设置
   - 现在可以开始使用翻译功能了

## 🔧 构建打包

### 使用构建脚本

```bash
python build.py
```

构建完成后，可执行文件将位于 `dist/` 目录下，文件名格式为 `翻译工具_v版本号.exe`。

### 手动构建

```bash
# 安装pyinstaller
pip install pyinstaller

# 执行打包
pyinstaller --noconfirm --onefile --noconsole \
    --icon=resources/icon.ico \
    --add-data "src/version_config.py;." \
    --add-data "resources;resources" \
    src/main.py
```

## 📁 项目结构

```
translator/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序入口
│   ├── translator.py      # 翻译核心功能
│   ├── settings_manager.py # 设置管理
│   ├── ui_manager.py      # 界面管理
│   └── version_config.py  # 版本配置
├── resources/             # 资源目录（图标等）
├── data/                  # 数据目录（自动创建）
├── log/                   # 日志目录（自动创建）
├── build.py               # 构建脚本
├── requirements.txt       # 依赖列表
└── README.md              # 说明文档
```

## ⌨️ 快捷键

默认快捷键（可在配置中自定义）：
- `Ctrl + Enter`：翻译
- `Ctrl + D`：清空文本
- `Ctrl + S`：截图翻译

## 📝 使用说明

1. **文本翻译**
   - 在源文本框输入或粘贴文本
   - 选择源语言和目标语言
   - 点击"翻译"按钮或使用快捷键

2. **截图翻译**
   - 点击"截图翻译"按钮或使用快捷键
   - 按住鼠标左键拖动选择要翻译的区域
   - 松开鼠标自动识别并翻译

3. **查看历史**
   - 切换到"历史记录"标签页
   - 可搜索历史翻译记录
   - 双击记录查看详细信息

4. **导出结果**
   - 翻译完成后点击"导出"按钮
   - 选择导出格式（TXT/Word/PDF/JSON）
   - 选择保存位置完成导出

## 🐛 常见问题

### Q: OCR识别不准确怎么办？
A: 确保截图区域清晰，避免模糊或倾斜的文字。可以尝试调整截图区域的大小和位置。

### Q: 翻译API调用失败？
A: 检查网络连接，确认百度翻译API的APP ID和密钥是否正确配置。

### Q: 程序无法启动？
A: 确保已安装所有依赖库，Tesseract-OCR已正确安装并配置环境变量。

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 📞 联系方式

- 项目地址：[GitHub链接]
- 作者：[作者名]
- 版本：[版本号]

---

**注意**：使用本工具需要有效的百度翻译API账号，翻译服务可能产生费用，请合理使用。