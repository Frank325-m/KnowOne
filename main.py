#!/usr/bin/env python3
"""
RAG 知识库问答系统命令行工具
提供向量数据库管理、系统测试和问答功能
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional, List

from config.logging_config import setup_logging, get_logger
from config.settings import settings
from core.loader_utils import (
    load_all_docs,
    clean_documents,
    split_documents,
    process_documents_pipeline,
    get_document_stats
)
from core.vector_utils import (
    create_vector_store,
    load_existing_vector_store,
    get_vector_store_info,
    search_knowledge,
    search_with_rerank
)
from core.llm_utils import (
    rag_chat,
    test_model_connection,
    get_model_info,
    simple_chat
)
from core.exceptions import RAGError, VectorDBNotFoundError

# 设置日志
logger = get_logger(__name__)


def create_vector_database(
    docs_dir: Optional[Path] = None,
    clean: bool = True,
    split: bool = True,
    force: bool = False
) -> bool:
    """
    创建向量数据库
    
    Args:
        docs_dir: 文档目录路径
        clean: 是否执行清理
        split: 是否执行分割
        force: 是否强制重新创建
        
    Returns:
        是否成功创建
    """
    try:
        if docs_dir is None:
            docs_dir = settings.docs_dir_abs
        
        logger.info(f"开始创建向量数据库，文档目录: {docs_dir}")
        
        # 检查向量数据库是否已存在
        vector_db_dir = settings.vector_db_dir_abs
        if vector_db_dir.exists() and not force:
            logger.warning(f"向量数据库已存在: {vector_db_dir}")
            logger.info("使用 --force 参数强制重新创建")
            return False
        
        # 处理文档管道
        logger.info("处理文档...")
        chunk_docs = process_documents_pipeline(
            folder_path=docs_dir,
            clean=clean,
            split=split
        )
        
        if not chunk_docs:
            logger.error("文档处理失败，没有可用的文档内容")
            return False
        
        # 创建向量数据库
        logger.info("创建向量数据库...")
        vector_store = create_vector_store(chunk_docs)
        
        if vector_store:
            count = vector_store._collection.count()
            logger.info(f"向量数据库创建成功，包含 {count} 个向量")
            return True
        else:
            logger.error("向量数据库创建失败")
            return False
            
    except Exception as e:
        logger.error(f"创建向量数据库失败: {e}")
        return False


def load_vector_database() -> bool:
    """
    加载向量数据库
    
    Returns:
        是否成功加载
    """
    try:
        logger.info("加载向量数据库...")
        vector_store = load_existing_vector_store()
        
        if vector_store:
            count = vector_store._collection.count()
            logger.info(f"向量数据库加载成功，包含 {count} 个向量")
            return True
        else:
            logger.error("向量数据库加载失败")
            return False
            
    except VectorDBNotFoundError as e:
        logger.error(f"向量数据库不存在: {e}")
        return False
    except Exception as e:
        logger.error(f"加载向量数据库失败: {e}")
        return False


def search_documents(
    query: str,
    use_rerank: bool = True,
    top_k: Optional[int] = None
) -> None:
    """
    搜索文档
    
    Args:
        query: 搜索查询
        use_rerank: 是否使用重排
        top_k: 返回结果数量
    """
    try:
        logger.info(f"搜索文档: '{query}'")
        
        if use_rerank:
            context, docs = search_with_rerank(query, top_k=top_k)
            search_type = "重排搜索"
        else:
            context, docs = search_knowledge(query, top_k=top_k)
            search_type = "普通搜索"
        
        print(f"\n{search_type} 结果:")
        print(f"找到 {len(docs)} 个相关文档")
        print(f"上下文长度: {len(context)} 字符")
        print("\n相关文档:")
        
        for i, doc in enumerate(docs, 1):
            print(f"\n[{i}] 来源: {doc.metadata.get('source', '未知')}")
            print(f"   内容: {doc.page_content[:200]}...")
        
        print(f"\n完整上下文:\n{context}")
        
    except Exception as e:
        logger.error(f"搜索文档失败: {e}")
        print(f"搜索失败: {e}")


def chat_with_rag(
    question: str,
    use_rerank: bool = True,
    model_name: Optional[str] = None
) -> None:
    """
    RAG 问答
    
    Args:
        question: 用户问题
        use_rerank: 是否使用重排
        model_name: 模型名称
    """
    try:
        logger.info(f"RAG 问答: '{question}'")
        
        response = rag_chat(
            question=question,
            use_rerank=use_rerank,
            model_name=model_name
        )
        
        print(f"\n问题: {question}")
        print(f"\n回答: {response}")
        
    except Exception as e:
        logger.error(f"RAG 问答失败: {e}")
        print(f"问答失败: {e}")


def simple_chat_with_model(
    question: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None
) -> None:
    """
    简单聊天（不使用 RAG）
    
    Args:
        question: 用户问题
        model_name: 模型名称
        temperature: 温度参数
    """
    try:
        logger.info(f"简单聊天: '{question}'")
        
        response = simple_chat(
            question=question,
            model_name=model_name,
            temperature=temperature
        )
        
        print(f"\n问题: {question}")
        print(f"\n回答: {response}")
        
    except Exception as e:
        logger.error(f"简单聊天失败: {e}")
        print(f"聊天失败: {e}")


def get_system_info(output_format: str = "text") -> None:
    """
    获取系统信息
    
    Args:
        output_format: 输出格式 (text/json)
    """
    try:
        logger.info("获取系统信息")
        
        # 获取模型信息
        model_info = get_model_info()
        
        # 获取向量数据库信息（使用超时）
        vector_info = {"exists": False, "message": "未加载"}
        try:
            vector_info = get_vector_store_info()
        except Exception as e:
            logger.warning(f"获取向量数据库信息失败: {e}")
            vector_info = {
                "exists": False,
                "message": f"加载失败: {str(e)[:100]}",
                "error": str(e)
            }
        
        # 测试模型连接（使用超时）
        model_test = {"success": False, "message": "未测试"}
        try:
            model_test = test_model_connection()
        except Exception as e:
            logger.warning(f"测试模型连接失败: {e}")
            model_test = {
                "success": False,
                "message": f"测试失败: {str(e)[:100]}",
                "error": str(e)
            }
        
        # 检查文档目录
        docs_dir = settings.docs_dir_abs
        docs_exists = docs_dir.exists()
        docs_files = []
        
        if docs_exists:
            docs_files = list(docs_dir.glob("*"))
        
        # 构建系统信息
        system_info = {
            "application": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "description": settings.APP_DESCRIPTION,
            },
            "directories": {
                "docs_directory": str(docs_dir),
                "docs_exists": docs_exists,
                "docs_file_count": len(docs_files),
                "vector_db_directory": str(settings.vector_db_dir_abs),
                "vector_db_exists": vector_info.get("exists", False),
                "model_cache_directory": str(settings.model_cache_dir_abs),
                "log_directory": str(settings.log_dir_abs),
            },
            "models": model_info,
            "vector_database": vector_info,
            "model_connection_test": model_test,
            "configuration": {
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "max_context_length": settings.MAX_CONTEXT_LENGTH,
                "default_top_k": settings.DEFAULT_TOP_K,
                "search_type": settings.SEARCH_TYPE,
                "web_port": settings.WEB_PORT,
                "web_host": settings.WEB_HOST,
            },
            "status": {
                "overall": "healthy" if all([
                    docs_exists,
                    vector_info.get("exists", False),
                    model_test.get("success", False)
                ]) else "warning",
            }
        }
        
        if output_format == "json":
            print(json.dumps(system_info, indent=2, ensure_ascii=False))
        else:
            # 文本格式输出
            print("\n" + "=" * 60)
            print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
            print("=" * 60)
            
            print(f"\n应用信息:")
            print(f"   名称: {system_info['application']['name']}")
            print(f"   版本: {system_info['application']['version']}")
            print(f"   描述: {system_info['application']['description']}")
            
            print(f"\n目录信息:")
            docs_status = "[存在]" if system_info['directories']['docs_exists'] else "[不存在]"
            print(f"   文档目录: {system_info['directories']['docs_directory']} {docs_status}")
            print(f"   文档数量: {system_info['directories']['docs_file_count']}")
            
            vector_status = "[存在]" if system_info['directories']['vector_db_exists'] else "[不存在]"
            print(f"   向量数据库: {system_info['directories']['vector_db_directory']} {vector_status}")
            
            print(f"\n模型信息:")
            print(f"   LLM模型: {system_info['models'].get('model_name', 'N/A')}")
            print(f"   嵌入模型: {system_info['models'].get('embedding_model', 'N/A')}")
            
            test_status = "[正常]" if system_info['model_connection_test'].get('success', False) else "[失败]"
            print(f"   模型连接: {test_status}")
            
            print(f"\n向量数据库:")
            if system_info['vector_database'].get('exists', False):
                print(f"   集合名称: {system_info['vector_database'].get('collection_name', 'N/A')}")
                print(f"   文档数量: {system_info['vector_database'].get('document_count', 0)}")
            else:
                print(f"   状态: {system_info['vector_database'].get('message', 'N/A')}")
            
            print(f"\n配置信息:")
            print(f"   文本块大小: {system_info['configuration']['chunk_size']} 字符")
            print(f"   块重叠大小: {system_info['configuration']['chunk_overlap']} 字符")
            print(f"   最大上下文: {system_info['configuration']['max_context_length']} 字符")
            print(f"   默认检索数: {system_info['configuration']['default_top_k']}")
            print(f"   搜索类型: {system_info['configuration']['search_type']}")
            
            print(f"\n系统状态:")
            overall = system_info['status']['overall']
            status_text = "[健康]" if overall == "healthy" else "[警告]" if overall == "warning" else "[错误]"
            print(f"   整体状态: {status_text}")
            
            print("\n" + "=" * 60)
        
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        print(f"获取系统信息失败: {e}")


def test_system() -> None:
    """
    测试系统功能
    """
    try:
        logger.info("测试系统功能")
        
        print("\n🧪 系统功能测试")
        print("=" * 40)
        
        # 1. 测试模型连接
        print("\n1. 测试模型连接...")
        model_test = test_model_connection()
        if model_test.get("success", False):
            print(f"   ✅ 模型连接正常: {model_test.get('model_name', 'N/A')}")
            print(f"      响应: {model_test.get('response', 'N/A')[:100]}...")
        else:
            print(f"   ❌ 模型连接失败: {model_test.get('error', '未知错误')}")
        
        # 2. 测试向量数据库
        print("\n2. 测试向量数据库...")
        vector_info = get_vector_store_info()
        if vector_info.get("exists", False):
            print(f"   ✅ 向量数据库正常")
            print(f"      集合: {vector_info.get('collection_name', 'N/A')}")
            print(f"      文档数: {vector_info.get('document_count', 0)}")
        else:
            print(f"   ⚠️ 向量数据库: {vector_info.get('message', 'N/A')}")
        
        # 3. 测试文档目录
        print("\n3. 测试文档目录...")
        docs_dir = settings.docs_dir_abs
        if docs_dir.exists():
            docs_files = list(docs_dir.glob("*"))
            print(f"   ✅ 文档目录正常: {len(docs_files)} 个文件")
        else:
            print(f"   ⚠️ 文档目录不存在: {docs_dir}")
        
        # 4. 测试 RAG 问答
        print("\n4. 测试 RAG 问答...")
        try:
            test_question = "测试 RAG 系统"
            response = rag_chat(test_question)
            print(f"   ✅ RAG 问答正常")
            print(f"      问题: {test_question}")
            print(f"      回答: {response[:100]}...")
        except Exception as e:
            print(f"   ❌ RAG 问答失败: {e}")
        
        print("\n" + "=" * 40)
        print("测试完成！")
        
    except Exception as e:
        logger.error(f"系统测试失败: {e}")
        print(f"系统测试失败: {e}")


def interactive_mode() -> None:
    """
    交互式模式
    """
    try:
        print(f"\n{settings.APP_NAME} 交互式模式")
        print("=" * 40)
        print("命令:")
        print("  q: 退出")
        print("  s: 搜索文档")
        print("  c: RAG 问答")
        print("  t: 简单聊天")
        print("  i: 系统信息")
        print("  d: 创建向量数据库")
        print("  l: 加载向量数据库")
        print("  test: 系统测试")
        print("=" * 40)
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'q':
                    print("退出交互式模式")
                    break
                
                elif command == 's':
                    query = input("搜索查询: ").strip()
                    if query:
                        use_rerank = input("使用重排? (y/n): ").strip().lower() == 'y'
                        search_documents(query, use_rerank=use_rerank)
                    else:
                        print("搜索查询不能为空")
                
                elif command == 'c':
                    question = input("问题: ").strip()
                    if question:
                        use_rerank = input("使用重排? (y/n): ").strip().lower() == 'y'
                        chat_with_rag(question, use_rerank=use_rerank)
                    else:
                        print("问题不能为空")
                
                elif command == 't':
                    question = input("问题: ").strip()
                    if question:
                        simple_chat_with_model(question)
                    else:
                        print("问题不能为空")
                
                elif command == 'i':
                    get_system_info()
                
                elif command == 'd':
                    force = input("强制重新创建? (y/n): ").strip().lower() == 'y'
                    if create_vector_database(force=force):
                        print("向量数据库创建成功")
                    else:
                        print("向量数据库创建失败")
                
                elif command == 'l':
                    if load_vector_database():
                        print("向量数据库加载成功")
                    else:
                        print("向量数据库加载失败")
                
                elif command == 'test':
                    test_system()
                
                else:
                    print(f"未知命令: {command}")
                    print("可用命令: q, s, c, t, i, d, l, test")
                    
            except KeyboardInterrupt:
                print("\n退出交互式模式")
                break
            except Exception as e:
                print(f"命令执行失败: {e}")
                
    except Exception as e:
        logger.error(f"交互式模式失败: {e}")
        print(f"交互式模式失败: {e}")


def main():
    """主函数"""
    # 初始化日志
    setup_logging()
    
    # 创建命令行解析器
    parser = argparse.ArgumentParser(
        description=settings.APP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s create          # 创建向量数据库
  %(prog)s load           # 加载向量数据库
  %(prog)s search "查询"   # 搜索文档
  %(prog)s chat "问题"     # RAG 问答
  %(prog)s info           # 显示系统信息
  %(prog)s test           # 测试系统功能
  %(prog)s interactive    # 进入交互式模式
        
Web 界面:
  python web_rag_app.py   # 启动 Web 应用
        """
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # create 命令: 创建向量数据库
    create_parser = subparsers.add_parser('create', help='创建向量数据库')
    create_parser.add_argument('--force', action='store_true', help='强制重新创建')
    create_parser.add_argument('--no-clean', action='store_true', help='跳过文档清理')
    create_parser.add_argument('--no-split', action='store_true', help='跳过文档分割')
    create_parser.add_argument('--docs-dir', type=Path, help='文档目录路径')
    
    # load 命令: 加载向量数据库
    load_parser = subparsers.add_parser('load', help='加载向量数据库')
    
    # search 命令: 搜索文档
    search_parser = subparsers.add_parser('search', help='搜索文档')
    search_parser.add_argument('query', help='搜索查询')
    search_parser.add_argument('--no-rerank', action='store_true', help='不使用重排')
    search_parser.add_argument('--top-k', type=int, help='返回结果数量')
    
    # chat 命令: RAG 问答
    chat_parser = subparsers.add_parser('chat', help='RAG 问答')
    chat_parser.add_argument('question', help='用户问题')
    chat_parser.add_argument('--no-rerank', action='store_true', help='不使用重排')
    chat_parser.add_argument('--model', help='模型名称')
    
    # simple-chat 命令: 简单聊天
    simple_chat_parser = subparsers.add_parser('simple-chat', help='简单聊天（不使用 RAG）')
    simple_chat_parser.add_argument('question', help='用户问题')
    simple_chat_parser.add_argument('--model', help='模型名称')
    simple_chat_parser.add_argument('--temperature', type=float, help='温度参数')
    
    # info 命令: 系统信息
    info_parser = subparsers.add_parser('info', help='显示系统信息')
    info_parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    
    # test 命令: 系统测试
    test_parser = subparsers.add_parser('test', help='测试系统功能')
    
    # interactive 命令: 交互式模式
    subparsers.add_parser('interactive', help='进入交互式模式')
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        logger.info(f"执行命令: {args.command}")
        
        if args.command == 'create':
            success = create_vector_database(
                docs_dir=args.docs_dir,
                clean=not args.no_clean,
                split=not args.no_split,
                force=args.force
            )
            sys.exit(0 if success else 1)
        
        elif args.command == 'load':
            success = load_vector_database()
            sys.exit(0 if success else 1)
        
        elif args.command == 'search':
            search_documents(
                query=args.query,
                use_rerank=not args.no_rerank,
                top_k=args.top_k
            )
        
        elif args.command == 'chat':
            chat_with_rag(
                question=args.question,
                use_rerank=not args.no_rerank,
                model_name=args.model
            )
        
        elif args.command == 'simple-chat':
            simple_chat_with_model(
                question=args.question,
                model_name=args.model,
                temperature=args.temperature
            )
        
        elif args.command == 'info':
            output_format = "json" if args.json else "text"
            get_system_info(output_format=output_format)
        
        elif args.command == 'test':
            test_system()
        
        elif args.command == 'interactive':
            interactive_mode()
        
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("命令被用户中断")
        print("\n命令被用户中断")
        sys.exit(0)
    except RAGError as e:
        logger.error(f"RAG 错误: {e}")
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"命令执行失败: {e}")
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()