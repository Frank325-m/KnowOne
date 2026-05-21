#!/usr/bin/env python3
"""
RAG 知识库问答系统 Web 应用入口点
基于 Gradio 的离线 RAG 系统 Web 界面
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.logging_config import setup_logging, get_logger
from web.app import launch_app

# 设置日志
logger = get_logger(__name__)


def main():
    """主函数"""
    try:
        # 初始化日志
        setup_logging()
        
        logger.info("=" * 60)
        logger.info("RAG 知识库问答系统 Web 应用启动")
        logger.info("=" * 60)
        
        # 启动 Web 应用
        launch_app()
        
    except KeyboardInterrupt:
        logger.info("应用被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()