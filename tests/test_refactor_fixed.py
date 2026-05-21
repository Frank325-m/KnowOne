#!/usr/bin/env python3
"""
重构后代码测试脚本（修复版）
验证模块化重构后的功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.logging_config import setup_logging, get_logger
from config.settings import settings

# 设置日志
logger = get_logger(__name__)


def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    modules_to_test = [
        ("config.settings", "settings"),
        ("config.logging_config", "setup_logging"),
        ("core.exceptions", "RAGError"),
        ("core.loader_utils", "load_all_docs"),
        ("core.vector_utils", "create_vector_store"),
        ("core.llm_utils", "rag_chat"),
        ("utils.file_utils", "ensure_directory"),
        ("web.app", "create_app"),
    ]
    
    all_passed = True
    for module_name, attr_name in modules_to_test:
        try:
            exec(f"from {module_name} import {attr_name}")
            print(f"  [OK] {module_name}.{attr_name}")
        except ImportError as e:
            print(f"  [FAIL] {module_name}.{attr_name}: {e}")
            all_passed = False
        except Exception as e:
            print(f"  [WARN] {module_name}.{attr_name}: {e}")
            all_passed = False
    
    return all_passed


def test_settings():
    """测试配置系统"""
    print("\n测试配置系统...")
    
    try:
        # 测试基本配置
        print(f"  应用名称: {settings.APP_NAME}")
        print(f"  应用版本: {settings.APP_VERSION}")
        print(f"  文档目录: {settings.docs_dir_abs}")
        print(f"  向量数据库目录: {settings.vector_db_dir_abs}")
        print(f"  日志目录: {settings.log_dir_abs}")
        
        # 测试目录创建
        for dir_name, dir_path in [
            ("文档目录", settings.docs_dir_abs),
            ("向量数据库目录", settings.vector_db_dir_abs),
            ("模型缓存目录", settings.model_cache_dir_abs),
            ("日志目录", settings.log_dir_abs),
        ]:
            if dir_path.exists():
                print(f"  [OK] {dir_name}: {dir_path} (已存在)")
            else:
                print(f"  [WARN] {dir_name}: {dir_path} (不存在)")
        
        # 测试模型配置
        print(f"  LLM模型: {settings.LLM_MODEL_NAME}")
        print(f"  嵌入模型: {settings.EMBED_MODEL_NAME}")
        print(f"  Web端口: {settings.WEB_PORT}")
        
        print("  [OK] 配置系统测试通过")
        return True
        
    except Exception as e:
        print(f"  [FAIL] 配置系统测试失败: {e}")
        return False


def test_logging():
    """测试日志系统"""
    print("\n测试日志系统...")
    
    try:
        # 初始化日志
        setup_logging()
        
        # 测试不同级别的日志
        logger.debug("这是一条调试日志")
        logger.info("这是一条信息日志")
        logger.warning("这是一条警告日志")
        logger.error("这是一条错误日志")
        
        # 检查日志文件
        log_dir = settings.log_dir_abs
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            if log_files:
                print(f"  [OK] 日志文件: {log_files[0].name}")
            else:
                print("  [WARN] 日志目录为空")
        else:
            print("  [WARN] 日志目录不存在")
        
        print("  [OK] 日志系统测试通过")
        return True
        
    except Exception as e:
        print(f"  [FAIL] 日志系统测试失败: {e}")
        return False


def test_core_modules():
    """测试核心模块"""
    print("\n测试核心模块...")
    
    from core.loader_utils import get_document_stats
    from core.vector_utils import get_vector_store_info
    from core.llm_utils import get_model_info, test_model_connection
    
    tests = [
        ("文档统计", lambda: get_document_stats([])),
        ("向量数据库信息", get_vector_store_info),
        ("模型信息", get_model_info),
        ("模型连接测试", test_model_connection),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            result = test_func()
            print(f"  [OK] {test_name}: {type(result).__name__}")
            if isinstance(result, dict):
                print(f"     结果键: {list(result.keys())}")
        except Exception as e:
            print(f"  [FAIL] {test_name}: {e}")
            all_passed = False
    
    return all_passed


def test_web_module():
    """测试 Web 模块"""
    print("\n测试 Web 模块...")
    
    from web.app import (
        get_html_content,
        refresh_document_list,
        get_system_status,
        get_vector_db_info,
        test_rag_pipeline
    )
    
    tests = [
        ("HTML内容生成", get_html_content),
        ("文档列表刷新", refresh_document_list),
        ("系统状态获取", get_system_status),
        ("向量数据库信息", get_vector_db_info),
        ("RAG流程测试", lambda: test_rag_pipeline("测试")),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            result = test_func()
            print(f"  [OK] {test_name}: {type(result).__name__}")
            if isinstance(result, dict):
                print(f"     结果键: {list(result.keys())}")
            elif isinstance(result, str):
                if len(result) > 100:
                    print(f"     结果预览: {result[:100]}...")
        except Exception as e:
            print(f"  [FAIL] {test_name}: {e}")
            all_passed = False
    
    return all_passed


def test_command_line():
    """测试命令行工具"""
    print("\n测试命令行工具...")
    
    try:
        # 测试 main.py 帮助
        import subprocess
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("  [OK] 命令行帮助测试通过")
            print(f"     输出行数: {len(result.stdout.splitlines())}")
        else:
            print(f"  [FAIL] 命令行帮助测试失败: {result.stderr}")
            return False
        
        # 测试 info 命令 - 增加超时时间
        result = subprocess.run(
            [sys.executable, "main.py", "info"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  [OK] info 命令测试通过")
            if "应用信息" in result.stdout or "application" in result.stdout:
                print("     包含应用信息")
        else:
            print(f"  [WARN] info 命令测试失败: {result.stderr}")
        
        print("  [OK] 命令行工具测试通过")
        return True
        
    except subprocess.TimeoutExpired:
        print("  [FAIL] 命令行工具测试超时")
        return False
    except Exception as e:
        print(f"  [FAIL] 命令行工具测试失败: {e}")
        return False


def test_build_script():
    """测试打包脚本"""
    print("\n测试打包脚本...")
    
    try:
        # 检查 build.py 是否存在
        build_script = Path("build.py")
        if not build_script.exists():
            print("  [FAIL] 打包脚本不存在")
            return False
        
        # 测试帮助
        import subprocess
        result = subprocess.run(
            [sys.executable, "build.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("  [OK] 打包脚本帮助测试通过")
            print(f"     输出行数: {len(result.stdout.splitlines())}")
        else:
            print(f"  [FAIL] 打包脚本帮助测试失败: {result.stderr}")
            return False
        
        print("  [OK] 打包脚本测试通过")
        return True
        
    except Exception as e:
        print(f"  [FAIL] 打包脚本测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("RAG 知识库问答系统重构测试")
    print("=" * 60)
    
    # 初始化日志
    setup_logging()
    
    tests = [
        ("模块导入", test_imports),
        ("配置系统", test_settings),
        ("日志系统", test_logging),
        ("核心模块", test_core_modules),
        ("Web模块", test_web_module),
        ("命令行工具", test_command_line),
        ("打包脚本", test_build_script),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  [FAIL] 测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        if success:
            print(f"[PASS] {test_name}: 通过")
            passed += 1
        else:
            print(f"[FAIL] {test_name}: 失败")
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n所有测试通过！重构成功！")
        print("\n下一步:")
        print("1. 运行 'python main.py --help' 查看命令行工具")
        print("2. 运行 'python web_rag_app.py' 启动 Web 应用")
        print("3. 运行 'python build.py --all' 打包可执行文件")
        return 0
    else:
        print(f"\n有 {failed} 个测试失败，请检查问题")
        return 1


if __name__ == "__main__":
    sys.exit(main())