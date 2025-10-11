import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 生成测试覆盖率报告
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        cov.stop()
        cov.save()
        cov.html_report(directory='coverage_report')
    except ImportError:
        print("Coverage module not installed. Skipping coverage report.")
        # 如果没有coverage，仍然运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
