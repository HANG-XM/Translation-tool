import os
import sys
import shutil
from src.version_config import VERSION_INFO

def build():
    """打包程序"""
    try:
        # 检查必要文件
        required_files = [
            'resources/icon.ico',
            'src/version_config.py',
            'src/main.py'
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"找不到必要文件: {file}")

        # 清理之前的构建
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # 创建dist目录
        os.makedirs('dist', exist_ok=True)
        
        # 执行打包命令，添加优化参数
        cmd = ('pyinstaller --noconfirm --onefile --noconsole '
               '--icon=resources/icon.ico '
               '--add-data "src/version_config.py;." '
               '--add-data "resources;resources" '
               '--exclude-module pandas '
               '--exclude-module numpy '
               '--exclude-module openpyxl '
               '--exclude-module docx '
               '--exclude-module coverage '
               '--exclude-module matplotlib '  # 排除matplotlib
               '--exclude-module scipy '  # 排除scipy
               '--noupx '  # 禁用UPX压缩以避免strip问题
               '--clean '  # 清理临时文件
               '--noconfirm '  # 覆盖输出
               'src/main.py')
        print(f"执行打包命令: {cmd}")
        result = os.system(cmd)
        
        if result != 0:
            raise RuntimeError("打包过程失败")
        
        # 重命名输出文件
        old_name = os.path.join('dist', 'main.exe')
        new_name = os.path.join('dist', f"翻译工具_v{VERSION_INFO['version']}.exe")
        if os.path.exists(old_name):
            os.rename(old_name, new_name)
            print(f"构建完成！输出文件：{new_name}")
        else:
            raise FileNotFoundError("打包输出文件未找到")
            
    except Exception as e:
        print(f"打包失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    build()
