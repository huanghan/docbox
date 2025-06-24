"""
测试运行器 - 统一运行所有测试
"""
import subprocess
import sys
import os

def run_test(test_file, description):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"🧪 运行测试: {description}")
    print(f"📁 文件: {test_file}")
    print('='*60)
    
    try:
        # 使用subprocess运行测试
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=False, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print(f"\n✅ {description} - 测试通过")
        else:
            print(f"\n❌ {description} - 测试失败 (退出码: {result.returncode})")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n💥 {description} - 运行异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 NoteDocs API 测试套件")
    print("自动运行所有测试用例")
    print("="*60)
    
    # 检查当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📂 测试目录: {current_dir}")
    
    # 测试文件列表
    tests = [
        ("test_category_simple.py", "分类API快速测试"),
        ("test_category_api.py", "分类API完整测试"),
        # 可以添加更多测试文件
        # ("test_document_api.py", "文档API测试"),
        # ("test_db.py", "数据库功能测试"),
    ]
    
    # 检查测试文件是否存在
    available_tests = []
    for test_file, description in tests:
        full_path = os.path.join(current_dir, test_file)
        if os.path.exists(full_path):
            available_tests.append((test_file, description))
        else:
            print(f"⚠️ 测试文件不存在: {test_file}")
    
    if not available_tests:
        print("❌ 没有找到可运行的测试文件")
        return
    
    print(f"\n📋 找到 {len(available_tests)} 个测试文件:")
    for test_file, description in available_tests:
        print(f"   - {test_file}: {description}")
    
    # 运行测试
    results = []
    for test_file, description in available_tests:
        success = run_test(test_file, description)
        results.append((description, success))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 总计: {passed + failed} 个测试")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！")
        sys.exit(0)
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 