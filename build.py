import os
import sys
import shutil
from version_config import VERSION_INFO

def build():
    """打包程序"""
    # 清理之前的构建
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # 执行打包命令
    cmd = f'pyinstaller --noconfirm --onefile --noconsole --icon=resources/icon.ico --add-data "version_config.py;." --add-data "resources;resources" main.py'
    os.system(cmd)
    
    # 重命名输出文件
    old_name = f"dist/main.exe"
    new_name = f"dist/翻译工具_v{VERSION_INFO['version']}.exe"
    if os.path.exists(old_name):
        os.rename(old_name, new_name)
    
    print(f"构建完成！输出文件：{new_name}")

if __name__ == '__main__':
    build()