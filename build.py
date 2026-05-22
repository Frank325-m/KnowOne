#!/usr/bin/env python3
"""
RAG 知识库问答系统打包脚本
使用 PyInstaller 将项目打包成可执行文件
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
SPEC_DIR = PROJECT_ROOT / "specs"

# 应用配置
APP_NAME = "RAG Knowledge Base Q&A System"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "main.py"
WEB_SCRIPT = "web_rag_app.py"

# 依赖包
REQUIRED_PACKAGES = [
    "gradio>=4.0.0",
    "langchain>=0.1.0",
    "langchain-community>=0.0.0",
    "langchain-text-splitters>=0.0.0",
    "chromadb>=0.4.0",
    "faiss-cpu>=1.7.0",
    "pymilvus>=2.3.0",
    "qdrant-client>=1.6.0",
    "sentence-transformers>=2.2.0",
    "pypdf>=3.0.0",
    "docx2txt>=0.8",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "ollama>=0.1.0",
    "requests>=2.28.0",
    "numpy>=1.24.0",
    "tqdm>=4.65.0",
]

# 隐藏导入
HIDDEN_IMPORTS = [
    "langchain_community.document_loaders",
    "langchain_community.embeddings",
    "langchain_community.vectorstores",
    "langchain_chroma",
    "langchain_milvus",
    "langchain_qdrant",
    "langchain_community.llms",
    "langchain_community.retrievers",
    "langchain_text_splitters",
    "chromadb",
    "chromadb.embeddings",
    "chromadb.utils",
    "sentence_transformers",
    "pydantic",
    "pydantic_settings",
    "gradio",
    "gradio.components",
    "gradio.routes",
    "gradio.themes",
    "ollama",
    "ollama._client",
    "ollama._types",
]

# 数据文件
DATA_FILES = [
    ("config", "config"),
    ("core", "core"),
    ("utils", "utils"),
    ("web", "web"),
    ("docs", "docs"),
    ("res", "res"),
    ("logs", "logs"),
]

# 排除模块
EXCLUDES = [
    "matplotlib",
    "scipy",
    "pandas",
    "tensorflow",
    "torch",
    "jax",
    "sklearn",
    "plotly",
    "bokeh",
    "dash",
    "flask",
    "django",
    "fastapi",
    "sqlalchemy",
    "sqlite3",
    "mysql",
    "postgresql",
    "mongo",
    "redis",
    "celery",
    "kafka",
    "grpc",
]

# 运行时钩子
RUNTIME_HOOKS = []


def print_header(title: str) -> None:
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def check_environment() -> bool:
    """检查环境"""
    print_header("检查环境")
    
    # 检查 Python 版本
    python_version = sys.version_info
    print(f"Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ 需要 Python 3.8 或更高版本")
        return False
    
    print("✅ Python 版本检查通过")
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller 版本: {PyInstaller.__version__}")
        print("✅ PyInstaller 检查通过")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False


def install_dependencies() -> bool:
    """安装依赖包"""
    print_header("安装依赖包")
    
    try:
        # 检查是否在虚拟环境中
        in_venv = sys.prefix != sys.base_prefix
        if not in_venv:
            print("⚠️  建议在虚拟环境中运行打包")
        
        # 安装依赖
        for package in REQUIRED_PACKAGES:
            print(f"检查/安装: {package}")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True
            )
        
        print("✅ 依赖包安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False


def clean_build_dirs() -> None:
    """清理构建目录"""
    print_header("清理构建目录")
    
    for dir_path in [BUILD_DIR, DIST_DIR, SPEC_DIR]:
        if dir_path.exists():
            print(f"删除目录: {dir_path}")
            shutil.rmtree(dir_path, ignore_errors=True)
    
    # 创建目录
    for dir_path in [BUILD_DIR, DIST_DIR, SPEC_DIR]:
        dir_path.mkdir(exist_ok=True)
    
    print("✅ 构建目录清理完成")


def collect_data_files() -> List[tuple]:
    """收集数据文件"""
    print_header("收集数据文件")
    
    data_files = []
    
    for src, dst in DATA_FILES:
        src_path = PROJECT_ROOT / src
        if src_path.exists():
            print(f"收集: {src} -> {dst}")
            data_files.append((str(src_path), dst))
        else:
            print(f"⚠️  源目录不存在: {src}")
    
    # 添加配置文件
    config_files = [
        (PROJECT_ROOT / ".env.example", "."),
        (PROJECT_ROOT / "README.md", "."),
        (PROJECT_ROOT / "requirements.txt", "."),
    ]
    
    for src, dst in config_files:
        if src.exists():
            print(f"收集: {src.name} -> {dst}")
            data_files.append((str(src), dst))
    
    print(f"✅ 收集了 {len(data_files)} 个数据文件")
    return data_files


def create_spec_file(
    script_name: str,
    app_name: str,
    data_files: List[tuple],
    hidden_imports: List[str],
    excludes: List[str],
    runtime_hooks: List[str]
) -> Path:
    """创建 spec 文件"""
    print_header(f"创建 {script_name} 的 spec 文件")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

block_cipher = None

# 数据文件
data_files = {data_files}

# 分析
a = Analysis(
    ['{script_name}'],
    pathex=[str(project_root)],
    binaries=[],
    datas=data_files,
    hiddenimports={hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks={runtime_hooks},
    excludes={excludes},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PyInstaller 配置
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={'False' if script_name == WEB_SCRIPT else 'True'},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# 收集
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{app_name}',
)
'''
    
    spec_file = SPEC_DIR / f"{script_name.replace('.py', '')}.spec"
    spec_file.write_text(spec_content, encoding="utf-8")
    
    print(f"✅ Spec 文件创建完成: {spec_file}")
    return spec_file


def build_executable(spec_file: Path) -> bool:
    """构建可执行文件"""
    print_header(f"构建可执行文件: {spec_file.name}")
    
    try:
        # 运行 PyInstaller
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 可执行文件构建成功")
            return True
        else:
            print(f"❌ 可执行文件构建失败: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 构建过程失败: {e}")
        return False


def create_launcher_scripts() -> None:
    """创建启动脚本"""
    print_header("创建启动脚本")
    
    # Windows 批处理脚本
    bat_content = '''@echo off
echo RAG 知识库问答系统
echo ===================
echo.
echo 1. 命令行工具 (main.exe)
echo 2. Web 应用 (web_rag_app.exe)
echo.
set /p choice="请选择 (1/2): "

if "%choice%"=="1" (
    echo 启动命令行工具...
    main.exe
) else if "%choice%"=="2" (
    echo 启动 Web 应用...
    web_rag_app.exe
) else (
    echo 无效选择
    pause
)
'''
    
    bat_file = DIST_DIR / "start_rag.bat"
    bat_file.write_text(bat_content, encoding="gbk")
    print(f"✅ 创建启动脚本: {bat_file}")
    
    # Linux/Mac shell 脚本
    sh_content = '''#!/bin/bash

echo "RAG 知识库问答系统"
echo "==================="
echo ""
echo "1. 命令行工具 (./main)"
echo "2. Web 应用 (./web_rag_app)"
echo ""
read -p "请选择 (1/2): " choice

if [ "$choice" = "1" ]; then
    echo "启动命令行工具..."
    ./main
elif [ "$choice" = "2" ]; then
    echo "启动 Web 应用..."
    ./web_rag_app
else
    echo "无效选择"
fi
'''
    
    sh_file = DIST_DIR / "start_rag.sh"
    sh_file.write_text(sh_content, encoding="utf-8")
    sh_file.chmod(0o755)
    print(f"✅ 创建启动脚本: {sh_file}")


def create_readme() -> None:
    """创建部署说明"""
    print_header("创建部署说明")
    
    readme_content = f'''# {APP_NAME} v{APP_VERSION} 部署说明

## 系统要求

- **操作系统**: Windows 7/8/10/11, Linux, macOS
- **Python**: 不需要安装 Python（已打包成可执行文件）
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 2GB 可用空间

## 文件结构

```
dist/
├── main.exe                    # 命令行工具
├── web_rag_app.exe            # Web 应用
├── start_rag.bat              # Windows 启动脚本
├── start_rag.sh               # Linux/Mac 启动脚本
├── config/                    # 配置文件目录
├── core/                      # 核心模块
├── utils/                     # 工具模块
├── web/                       # Web 模块
├── docs/                      # 文档目录
├── res/                       # 资源目录
├── logs/                      # 日志目录
├── .env.example               # 环境变量示例
├── README.md                  # 项目说明
└── requirements.txt           # 依赖包列表
```

## 快速开始

### Windows 用户
1. 双击 `start_rag.bat`
2. 选择启动方式：
   - 输入 `1` 启动命令行工具
   - 输入 `2` 启动 Web 应用

### Linux/Mac 用户
1. 打开终端
2. 运行: `chmod +x start_rag.sh`
3. 运行: `./start_rag.sh`
4. 选择启动方式（同上）

## 使用说明

### 命令行工具 (main.exe)
```bash
# 显示帮助
main.exe --help

# 创建向量数据库
main.exe create

# 加载向量数据库
main.exe load

# 搜索文档
main.exe search "搜索查询"

# RAG 问答
main.exe chat "用户问题"

# 显示系统信息
main.exe info

# 测试系统功能
main.exe test

# 交互式模式
main.exe interactive
```

### Web 应用 (web_rag_app.exe)
1. 启动 Web 应用
2. 打开浏览器访问: http://localhost:7801
3. 功能包括：
   - 文档上传和管理
   - 知识库构建
   - 智能问答
   - 系统状态监控

## 配置说明

### 环境变量
复制 `.env.example` 为 `.env` 并修改配置：

```env
# 应用配置
APP_NAME="RAG Knowledge Base Q&A System"
APP_VERSION="1.0.0"

# 模型配置
LLM_MODEL_NAME="qwen:4b"
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4096

# 嵌入模型配置
EMBED_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
EMBED_MODEL_DEVICE="cpu"

# Web 服务配置
WEB_HOST="0.0.0.0"
WEB_PORT=7801
WEB_DEBUG=false
WEB_SHARE=false

# 日志配置
LOG_LEVEL="INFO"
```

### 目录配置
- `docs/`: 存放上传的文档文件
- `res/chroma_db/`: 向量数据库存储
- `model_cache/`: 模型缓存
- `logs/`: 日志文件

## 常见问题

### 1. 启动时提示缺少 DLL
- 确保系统已安装 Visual C++ Redistributable
- Windows 用户可下载安装: https://aka.ms/vs/17/release/vc_redist.x64.exe

### 2. Web 应用无法访问
- 检查防火墙设置，确保端口 7801 已开放
- 尝试使用 `http://127.0.0.1:7801` 访问

### 3. 模型加载失败
- 确保网络连接正常（首次运行需要下载模型）
- 检查 `model_cache/` 目录权限

### 4. 文档处理失败
- 确保文档格式为: .txt, .pdf, .docx
- 检查文档编码（建议使用 UTF-8）

## 技术支持

- 项目仓库: [项目地址]
- 问题反馈: [问题跟踪]
- 文档: [文档链接]

## 许可证

本项目基于 MIT 许可证开源。

---

**注意**: 首次运行时，系统会自动下载必要的模型文件，请确保网络连接正常。
'''
    
    readme_file = DIST_DIR / "DEPLOYMENT_README.md"
    readme_file.write_text(readme_content, encoding="utf-8")
    print(f"✅ 创建部署说明: {readme_file}")


def verify_build() -> bool:
    """验证构建结果"""
    print_header("验证构建结果")
    
    required_files = [
        DIST_DIR / "main.exe",
        DIST_DIR / "web_rag_app.exe",
        DIST_DIR / "start_rag.bat",
        DIST_DIR / "start_rag.sh",
        DIST_DIR / "DEPLOYMENT_README.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file_path.name}: {size:,} bytes")
        else:
            print(f"❌ 文件不存在: {file_path.name}")
            all_exist = False
    
    # 检查目录
    required_dirs = ["config", "core", "utils", "web"]
    for dir_name in required_dirs:
        dir_path = DIST_DIR / dir_name
        if dir_path.exists():
            print(f"✅ 目录存在: {dir_name}")
        else:
            print(f"❌ 目录不存在: {dir_name}")
            all_exist = False
    
    if all_exist:
        print("✅ 构建验证通过")
        return True
    else:
        print("❌ 构建验证失败")
        return False


def create_zip_package() -> None:
    """创建 ZIP 包"""
    print_header("创建 ZIP 包")
    
    import zipfile
    import datetime
    
    # 创建版本号
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"rag_knowledge_base_v{APP_VERSION}_{timestamp}.zip"
    zip_path = PROJECT_ROOT / zip_name
    
    # 创建 ZIP 文件
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加 dist 目录内容
        for root, dirs, files in os.walk(DIST_DIR):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(DIST_DIR)
                zipf.write(file_path, arcname)
                print(f"添加: {arcname}")
    
    zip_size = zip_path.stat().st_size
    print(f"✅ ZIP 包创建完成: {zip_path.name} ({zip_size:,} bytes)")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RAG 知识库问答系统打包工具")
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--install", action="store_true", help="安装依赖包")
    parser.add_argument("--build", action="store_true", help="构建可执行文件")
    parser.add_argument("--package", action="store_true", help="创建 ZIP 包")
    parser.add_argument("--all", action="store_true", help="执行所有步骤")
    parser.add_argument("--verify", action="store_true", help="验证构建结果")
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        # 执行所有步骤
        if args.all or args.clean:
            clean_build_dirs()
        
        if args.all or args.install:
            if not check_environment():
                return
            if not install_dependencies():
                return
        
        if args.all or args.build:
            # 收集数据文件
            data_files = collect_data_files()
            
            # 构建命令行工具
            main_spec = create_spec_file(
                script_name=MAIN_SCRIPT,
                app_name="main",
                data_files=data_files,
                hidden_imports=HIDDEN_IMPORTS,
                excludes=EXCLUDES,
                runtime_hooks=RUNTIME_HOOKS
            )
            
            if not build_executable(main_spec):
                return
            
            # 构建 Web 应用
            web_spec = create_spec_file(
                script_name=WEB_SCRIPT,
                app_name="web_rag_app",
                data_files=data_files,
                hidden_imports=HIDDEN_IMPORTS,
                excludes=EXCLUDES,
                runtime_hooks=RUNTIME_HOOKS
            )
            
            if not build_executable(web_spec):
                return
            
            # 创建启动脚本和说明
            create_launcher_scripts()
            create_readme()
        
        if args.all or args.verify:
            if not verify_build():
                return
        
        if args.all or args.package:
            create_zip_package()
        
        print_header("打包完成")
        print(f"可执行文件位置: {DIST_DIR}")
        print(f"启动脚本: {DIST_DIR / 'start_rag.bat'} (Windows)")
        print(f"启动脚本: {DIST_DIR / 'start_rag.sh'} (Linux/Mac)")
        print(f"Web 应用访问: http://localhost:7801")
        
    except KeyboardInterrupt:
        print("\n打包被用户中断")
    except Exception as e:
        print(f"打包失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()