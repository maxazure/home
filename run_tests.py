import unittest
import sys
import os

# 设置测试发现的起始目录
start_dir = 'tests'

def run_all_tests():
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 发现所有测试
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 创建测试运行器
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 运行测试
    result = runner.run(suite)
    
    # 打印测试统计
    print("\n=== 测试统计 ===")
    print(f"运行的测试用例总数: {result.testsRun}")
    print(f"成功的测试用例数: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败的测试用例数: {len(result.failures)}")
    print(f"错误的测试用例数: {len(result.errors)}")
    
    # 如果有失败的测试，返回非零状态码
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    # 确保在正确的目录中运行测试
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_all_tests() 