#!/usr/bin/env python3
"""
修复导入问题脚本
将相对导入改为绝对导入
"""

import os
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 需要修复的文件
FILES_TO_FIX = [
    "core/loader_utils.py",
    "core/vector_utils.py",
    "core/llm_utils.py",
    "utils/file_utils.py",
    "web/app.py",
]

# 导入映射
IMPORT_MAPPINGS = {
    # 相对导入 -> 绝对导入
    "from ..config.settings import": "from config.settings import",
    "from ..config.logging_config import": "from config.logging_config import",
    "from .exceptions import": "from core.exceptions import",
    "from ..utils.file_utils import": "from utils.file_utils import",
    "from ...config.settings import": "from config.settings import",
    "from ...config.logging_config import": "from config.logging_config import",
    "from ..core.": "from core.",
    "from ...utils.": "from utils.",
}


def fix_imports_in_file(file_path: Path):
    """修复文件中的导入"""
    print(f"修复文件: {file_path}")
    
    if not file_path.exists():
        print(f"  文件不存在: {file_path}")
        return
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复导入
    original_content = content
    for old_import, new_import in IMPORT_MAPPINGS.items():
        content = content.replace(old_import, new_import)
    
    # 检查是否有变化
    if content != original_content:
        # 备份原文件
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  已创建备份: {backup_path}")
        
        # 写入修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  导入已修复")
        
        # 显示修复的导入
        lines_original = original_content.split('\n')
        lines_fixed = content.split('\n')
        
        for i, (orig, fixed) in enumerate(zip(lines_original, lines_fixed)):
            if orig != fixed and ('import' in orig or 'from' in orig):
                print(f"    第{i+1}行: {orig.strip()}")
                print(f"          -> {fixed.strip()}")
    else:
        print(f"  无需修复")


def main():
    """主函数"""
    print("开始修复导入问题...")
    print("=" * 60)
    
    for file_rel_path in FILES_TO_FIX:
        file_path = PROJECT_ROOT / file_rel_path
        fix_imports_in_file(file_path)
        print()
    
    print("=" * 60)
    print("导入修复完成！")
    
    # 测试修复
    print("\n测试修复后的导入...")
    test_imports = [
        "from config.settings import settings",
        "from config.logging_config import setup_logging",
        "from core.exceptions import RAGError",
        "from core.loader_utils import load_all_docs",
        "from core.vector_utils import create_vector_store",
        "from core.llm_utils import rag_chat",
        "from utils.file_utils import ensure_directory",
        "from web.app import create_app",
    ]
    
    for import_stmt in test_imports:
        try:
            exec(import_stmt)
            print(f"  [OK] {import_stmt}")
        except Exception as e:
            print(f"  [FAIL] {import_stmt}: {e}")


if __name__ == "__main__":
    main()