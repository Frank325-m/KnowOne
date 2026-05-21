"""
Web 应用主模块
基于 Gradio 的 RAG 知识库问答系统 Web 界面
"""

import os
import datetime
import gradio as gr
from gradio import ChatMessage
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging

from config.settings import settings
from config.logging_config import get_logger, setup_logging
from core.llm_utils import rag_chat, test_model_connection, get_model_info
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
    get_vector_store_info
)
from utils.file_utils import (
    ensure_directory,
    get_file_size,
    format_file_size,
    is_supported_file,
    list_files_in_directory,
    copy_file_safe
)

# 获取日志记录器
logger = get_logger(__name__)


def get_html_content() -> str:
    """
    获取文档目录下的所有文档文件，返回HTML格式内容
    
    Returns:
        HTML格式的文档列表
    """
    try:
        docs_dir = settings.docs_dir_abs
        
        if not docs_dir.exists():
            return """
            <div style="color: #666; font-style: italic; padding: 20px; text-align: center;">
                📁 文档目录不存在
            </div>
            """
        
        # 列出所有支持的文件
        all_files = list_files_in_directory(
            docs_dir,
            extensions=settings.SUPPORTED_EXTENSIONS,
            recursive=False
        )
        
        if not all_files:
            return """
            <div style="color: #666; font-style: italic; padding: 20px; text-align: center;">
                📄 暂无文档，请上传文档开始构建知识库
            </div>
            """
        
        # 构建HTML内容
        html_content = """
        <div style="max-height: 400px; overflow-y: auto; padding: 10px; background: #f8f9fa; border-radius: 8px;">
        """
        
        for i, file_path in enumerate(all_files, 1):
            try:
                file_size = get_file_size(file_path)
                size_str = format_file_size(file_size)
                file_name = file_path.name
                file_ext = file_path.suffix.lower()
                
                # 根据文件类型设置图标
                if file_ext == ".pdf":
                    icon = "📕"
                elif file_ext == ".docx":
                    icon = "📘"
                elif file_ext == ".txt":
                    icon = "📝"
                else:
                    icon = "📄"
                
                # 添加文件项
                html_content += f"""
                <div style="
                    padding: 12px 15px; 
                    margin: 8px 0; 
                    background: white; 
                    border-radius: 6px; 
                    border-left: 4px solid #4CAF50;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    display: flex; 
                    justify-content: space-between;
                    align-items: center;
                    transition: all 0.3s ease;
                ">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.2em;">{icon}</span>
                        <div>
                            <div style="font-weight: 600; color: #333;">{file_name}</div>
                            <div style="font-size: 0.85em; color: #666; margin-top: 2px;">
                                {file_ext.upper().replace('.', '')} 文件
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: 500; color: #2196F3;">{size_str}</div>
                        <div style="font-size: 0.8em; color: #888; margin-top: 2px;">
                            文档 #{i}
                        </div>
                    </div>
                </div>
                """
                
            except Exception as e:
                logger.warning(f"处理文件信息失败 {file_path}: {e}")
                continue
        
        # 添加统计信息
        total_files = len(all_files)
        total_size = sum(get_file_size(f) for f in all_files)
        total_size_str = format_file_size(total_size)
        
        html_content += f"""
        <div style="
            margin-top: 15px;
            padding: 10px;
            background: #e8f5e9;
            border-radius: 6px;
            font-size: 0.9em;
            color: #2e7d32;
            text-align: center;
        ">
            📊 总计: {total_files} 个文档 | {total_size_str}
        </div>
        """
        
        html_content += "</div>"
        
        logger.debug(f"生成HTML文档列表，包含 {total_files} 个文件")
        return html_content
        
    except Exception as e:
        logger.error(f"获取HTML内容失败: {e}")
        return f"""
        <div style="color: #f44336; padding: 20px; text-align: center;">
            ❌ 获取文档列表失败: {str(e)}
        </div>
        """


def upload_and_build_knowledge(files: List[gr.File]) -> Tuple[str, str]:
    """
    上传文档并自动构建知识库
    
    Args:
        files: 上传的文件列表
        
    Returns:
        tuple: (构建状态信息, 更新后的HTML内容)
    """
    try:
        if not files:
            logger.warning("未选择任何文件")
            return "⚠️ 未选择任何文件", get_html_content()
        
        docs_dir = settings.docs_dir_abs
        ensure_directory(docs_dir)
        
        saved_files = []
        failed_files = []
        
        # 保存上传的文件
        for file in files:
            try:
                file_path = Path(file.name)
                file_name = file_path.name
                save_path = docs_dir / file_name
                
                # 检查文件是否已存在
                if save_path.exists():
                    # 创建备份
                    backup_name = f"{save_path.stem}_backup{save_path.suffix}"
                    backup_path = docs_dir / backup_name
                    copy_file_safe(save_path, backup_path, overwrite=True)
                    logger.info(f"文件已存在，创建备份: {backup_name}")
                
                # 保存文件
                with open(file, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                
                saved_files.append(file_name)
                logger.info(f"文件保存成功: {file_name}")
                
            except Exception as e:
                failed_files.append((file_path.name, str(e)))
                logger.error(f"文件保存失败 {file_path.name}: {e}")
        
        # 构建状态信息
        status_msg = f"✅ 成功保存 {len(saved_files)} 个文件"
        if failed_files:
            status_msg += f"，失败 {len(failed_files)} 个文件"
        
        # 处理文档并构建向量数据库
        try:
            logger.info("开始处理文档并构建向量数据库")
            
            # 1. 加载所有文档
            all_docs = load_all_docs(docs_dir)
            if not all_docs:
                return f"{status_msg}\n⚠️ 文档加载失败，没有可用的文档内容", get_html_content()
            
            doc_stats = get_document_stats(all_docs)
            status_msg += f"\n📄 加载 {doc_stats['count']} 个文档片段，总字符数: {doc_stats['total_chars']}"
            
            # 2. 清理文档
            cleaned_docs = clean_documents(all_docs)
            if not cleaned_docs:
                return f"{status_msg}\n⚠️ 文档清理失败，清理后没有可用的文档内容", get_html_content()
            
            # 3. 分割文档
            chunk_docs = split_documents(cleaned_docs)
            if not chunk_docs:
                return f"{status_msg}\n⚠️ 文档分割失败，分割后没有可用的文档内容", get_html_content()
            
            status_msg += f"\n✂️ 分割为 {len(chunk_docs)} 个文本块"
            
            # 4. 创建向量数据库
            vector_store = create_vector_store(chunk_docs)
            if vector_store:
                count = vector_store._collection.count()
                status_msg += f"\n🔍 向量数据库创建成功，包含 {count} 个向量"
            
            status_msg += "\n🎉 知识库构建完成！"
            logger.info("知识库构建成功")
            
        except Exception as e:
            error_msg = f"知识库构建失败: {str(e)}"
            logger.error(error_msg)
            status_msg += f"\n❌ {error_msg}"
        
        # 返回构建状态和更新后的文档列表
        return status_msg, get_html_content()
        
    except Exception as e:
        error_msg = f"上传和处理文件失败: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}", get_html_content()


def chat_response(message: str, history: List[ChatMessage]) -> List[ChatMessage]:
    """
    处理用户输入并返回模型回复
    
    Args:
        message: 用户输入的消息
        history: 对话历史记录
        
    Returns:
        更新后的对话历史
    """
    try:
        if not message or not message.strip():
            logger.warning("聊天消息为空")
            return history or []
        
        logger.info(f"处理用户消息: '{message}'")
        
        # 如果 history 是 None，初始化为空列表
        if history is None:
            history = []
        
        # 添加用户消息
        history.append(ChatMessage(role="user", content=message))
        
        try:
            # 获取模型回复
            response = rag_chat(message)
            logger.info(f"模型回复完成，长度: {len(response)} 字符")
            
        except Exception as e:
            error_msg = f"模型回复失败: {str(e)}"
            logger.error(error_msg)
            response = f"❌ {error_msg}"
        
        # 添加助手回复
        history.append(ChatMessage(role="assistant", content=response))
        
        return history
        
    except Exception as e:
        logger.error(f"聊天响应处理失败: {e}")
        # 返回原始历史或空列表
        return history or []


def refresh_document_list() -> str:
    """
    刷新文档列表
    
    Returns:
        更新后的HTML内容
    """
    try:
        logger.info("刷新文档列表")
        html_content = get_html_content()
        logger.info("文档列表刷新完成")
        return html_content
    except Exception as e:
        logger.error(f"刷新文档列表失败: {e}")
        return f"""
        <div style="color: #f44336; padding: 20px; text-align: center;">
            ❌ 刷新文档列表失败: {str(e)}
        </div>
        """


def get_system_status() -> Dict[str, Any]:
    """
    获取系统状态信息
    
    Returns:
        系统状态信息字典
    """
    try:
        logger.info("获取系统状态")
        
        # 检查文档目录
        docs_dir = settings.docs_dir_abs
        docs_exists = docs_dir.exists()
        docs_files = []
        
        if docs_exists:
            docs_files = list_files_in_directory(
                docs_dir,
                extensions=settings.SUPPORTED_EXTENSIONS,
                recursive=False
            )
        
        # 检查向量数据库
        vector_db_info = get_vector_store_info()
        
        # 测试模型连接
        model_test = test_model_connection()
        
        # 构建状态信息
        status = {
            "system": {
                "app_name": settings.APP_NAME,
                "app_version": settings.APP_VERSION,
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                "working_directory": str(Path.cwd()),
                "log_directory": str(settings.log_dir_abs),
            },
            "directories": {
                "docs_directory": str(docs_dir),
                "docs_exists": docs_exists,
                "docs_file_count": len(docs_files),
                "vector_db_directory": str(settings.vector_db_dir_abs),
                "vector_db_exists": vector_db_info.get("exists", False),
                "model_cache_directory": str(settings.model_cache_dir_abs),
            },
            "models": {
                "llm_model": settings.LLM_MODEL_NAME,
                "embedding_model": settings.EMBED_MODEL_NAME,
                "model_connection_test": model_test.get("success", False),
                "model_test_message": model_test.get("message", "未测试"),
            },
            "vector_database": vector_db_info,
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
                    vector_db_info.get("exists", False),
                    model_test.get("success", False)
                ]) else "warning",
                "timestamp": datetime.datetime.now().isoformat(),
            }
        }
        
        logger.debug(f"系统状态: {status}")
        return status
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return {
            "error": str(e),
            "status": "error",
            "timestamp": datetime.datetime.now().isoformat(),
        }


def get_vector_db_info() -> Dict[str, Any]:
    """
    获取向量数据库信息
    
    Returns:
        向量数据库信息字典
    """
    try:
        logger.info("获取向量数据库信息")
        info = get_vector_store_info()
        logger.debug(f"向量数据库信息: {info}")
        return info
    except Exception as e:
        logger.error(f"获取向量数据库信息失败: {e}")
        return {
            "error": str(e),
            "exists": False,
            "message": "获取向量数据库信息失败"
        }


def test_rag_pipeline(question: str = "测试RAG流程") -> Dict[str, Any]:
    """
    测试RAG流程
    
    Args:
        question: 测试问题
        
    Returns:
        测试结果字典
    """
    try:
        logger.info(f"测试RAG流程，问题: '{question}'")
        
        result = {
            "question": question,
            "timestamp": datetime.datetime.now().isoformat(),
            "steps": {},
            "success": False,
            "message": ""
        }
        
        # 1. 测试模型连接
        try:
            model_test = test_model_connection()
            result["steps"]["model_connection"] = model_test
            logger.debug(f"模型连接测试: {model_test.get('success', False)}")
        except Exception as e:
            result["steps"]["model_connection"] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"模型连接测试失败: {e}")
        
        # 2. 测试向量数据库
        try:
            vector_info = get_vector_store_info()
            result["steps"]["vector_database"] = vector_info
            logger.debug(f"向量数据库测试: {vector_info.get('exists', False)}")
        except Exception as e:
            result["steps"]["vector_database"] = {
                "exists": False,
                "error": str(e)
            }
            logger.error(f"向量数据库测试失败: {e}")
        
        # 3. 测试RAG问答
        try:
            if question:
                response = rag_chat(question)
                result["steps"]["rag_chat"] = {
                    "success": True,
                    "response_length": len(response),
                    "response_preview": response[:200] + "..." if len(response) > 200 else response
                }
                logger.debug(f"RAG问答测试成功，响应长度: {len(response)}")
            else:
                result["steps"]["rag_chat"] = {
                    "success": False,
                    "error": "测试问题为空"
                }
        except Exception as e:
            result["steps"]["rag_chat"] = {
                "success": False,
                "error": str(e)
            }
            logger.error(f"RAG问答测试失败: {e}")
        
        # 判断整体成功状态
        all_success = all(
            step.get("success", step.get("exists", False))
            for step in result["steps"].values()
            if isinstance(step, dict)
        )
        
        result["success"] = all_success
        result["message"] = "RAG流程测试完成" if all_success else "RAG流程测试失败"
        
        logger.info(f"RAG流程测试完成，结果: {all_success}")
        return result
        
    except Exception as e:
        logger.error(f"RAG流程测试失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "RAG流程测试失败",
            "timestamp": datetime.datetime.now().isoformat(),
        }


def format_status_html(status: Dict[str, Any]) -> str:
    """
    格式化系统状态为HTML
    
    Args:
        status: 系统状态字典
        
    Returns:
        HTML格式的系统状态
    """
    try:
        # 确定整体状态颜色
        overall_status = status.get("status", {}).get("overall", "unknown")
        if overall_status == "healthy":
            status_color = "#4CAF50"
            status_icon = "✅"
        elif overall_status == "warning":
            status_color = "#FF9800"
            status_icon = "⚠️"
        else:
            status_color = "#F44336"
            status_icon = "❌"
        
        html = f"""
        <div style="
            padding: 20px; 
            background: #f8f9fa; 
            border-radius: 10px; 
            border: 1px solid #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
        ">
            <div style="
                display: flex; 
                align-items: center; 
                margin-bottom: 20px; 
                padding-bottom: 15px; 
                border-bottom: 2px solid {status_color};
            ">
                <span style="font-size: 1.5em; margin-right: 10px;">{status_icon}</span>
                <h2 style="margin: 0; color: #333;">系统状态</h2>
                <span style="
                    margin-left: auto; 
                    padding: 5px 15px; 
                    background: {status_color}; 
                    color: white; 
                    border-radius: 20px; 
                    font-size: 0.9em; 
                    font-weight: 600;
                ">
                    {overall_status.upper()}
                </span>
            </div>
        """
        
        # 系统信息
        system_info = status.get("system", {})
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #555; margin-bottom: 10px;">📱 应用信息</h3>
            <div style="
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 10px;
            ">
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">应用名称</div>
                    <div style="font-weight: 600; color: #333;">{system_info.get('app_name', 'N/A')}</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">版本</div>
                    <div style="font-weight: 600; color: #333;">{system_info.get('app_version', 'N/A')}</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">Python版本</div>
                    <div style="font-weight: 600; color: #333;">{system_info.get('python_version', 'N/A')}</div>
                </div>
            </div>
        </div>
        """
        
        # 目录信息
        dir_info = status.get("directories", {})
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #555; margin-bottom: 10px;">📁 目录信息</h3>
            <div style="
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 10px;
            ">
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">文档目录</div>
                    <div style="font-weight: 600; color: #333; word-break: break-all;">{dir_info.get('docs_directory', 'N/A')}</div>
                    <div style="font-size: 0.85em; color: #888; margin-top: 5px;">
                        📄 {dir_info.get('docs_file_count', 0)} 个文档 | 
                        {'✅ 存在' if dir_info.get('docs_exists', False) else '❌ 不存在'}
                    </div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">向量数据库目录</div>
                    <div style="font-weight: 600; color: #333; word-break: break-all;">{dir_info.get('vector_db_directory', 'N/A')}</div>
                    <div style="font-size: 0.85em; color: #888; margin-top: 5px;">
                        {'✅ 存在' if dir_info.get('vector_db_exists', False) else '❌ 不存在'}
                    </div>
                </div>
            </div>
        </div>
        """
        
        # 模型信息
        model_info = status.get("models", {})
        model_test = model_info.get("model_connection_test", False)
        model_test_color = "#4CAF50" if model_test else "#F44336"
        model_test_icon = "✅" if model_test else "❌"
        
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #555; margin-bottom: 10px;">🤖 模型信息</h3>
            <div style="
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 10px;
            ">
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">LLM模型</div>
                    <div style="font-weight: 600; color: #333;">{model_info.get('llm_model', 'N/A')}</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">嵌入模型</div>
                    <div style="font-weight: 600; color: #333;">{model_info.get('embedding_model', 'N/A')}</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">模型连接测试</div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.2em;">{model_test_icon}</span>
                        <span style="font-weight: 600; color: {model_test_color};">{model_info.get('model_test_message', 'N/A')}</span>
                    </div>
                </div>
            </div>
        </div>
        """
        
        # 向量数据库信息
        vector_info = status.get("vector_database", {})
        vector_exists = vector_info.get("exists", False)
        vector_color = "#4CAF50" if vector_exists else "#F44336"
        vector_icon = "✅" if vector_exists else "❌"
        
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #555; margin-bottom: 10px;">🔍 向量数据库</h3>
            <div style="background: white; padding: 15px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <span style="font-size: 1.2em;">{vector_icon}</span>
                    <span style="font-weight: 600; color: {vector_color};">
                        {vector_info.get('message', '向量数据库状态')}
                    </span>
                </div>
        """
        
        if vector_exists:
            html += f"""
                <div style="
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 10px; 
                    margin-top: 10px;
                ">
                    <div>
                        <div style="font-size: 0.9em; color: #666;">集合名称</div>
                        <div style="font-weight: 600; color: #333;">{vector_info.get('collection_name', 'N/A')}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: #666;">文档数量</div>
                        <div style="font-weight: 600; color: #333;">{vector_info.get('document_count', 0)}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9em; color: #666;">嵌入模型</div>
                        <div style="font-weight: 600; color: #333;">{vector_info.get('embedding_model', 'N/A')}</div>
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        # 配置信息
        config_info = status.get("configuration", {})
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #555; margin-bottom: 10px;">⚙️ 配置信息</h3>
            <div style="
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 10px;
            ">
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">文本块大小</div>
                    <div style="font-weight: 600; color: #333;">{config_info.get('chunk_size', 0)} 字符</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">块重叠大小</div>
                    <div style="font-weight: 600; color: #333;">{config_info.get('chunk_overlap', 0)} 字符</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">最大上下文长度</div>
                    <div style="font-weight: 600; color: #333;">{config_info.get('max_context_length', 0)} 字符</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">默认检索数量</div>
                    <div style="font-weight: 600; color: #333;">{config_info.get('default_top_k', 0)}</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">搜索类型</div>
                    <div style="font-weight: 600; color: #333;">{config_info.get('search_type', 'N/A')}</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.9em; color: #666;">Web服务端口</div>
                    <div style="font-weight: 600; color: #333;">{config_info.get('web_port', 0)}</div>
                </div>
            </div>
        </div>
        """
        
        # 时间戳
        timestamp = status.get("status", {}).get("timestamp", "N/A")
        html += f"""
        <div style="
            margin-top: 20px; 
            padding-top: 15px; 
            border-top: 1px solid #e0e0e0; 
            text-align: center; 
            font-size: 0.85em; 
            color: #888;
        ">
            状态更新时间: {timestamp}
        </div>
        """
        
        html += "</div>"
        return html
        
    except Exception as e:
        logger.error(f"格式化状态HTML失败: {e}")
        return f"""
        <div style="color: #f44336; padding: 20px; text-align: center;">
            ❌ 格式化系统状态失败: {str(e)}
        </div>
        """


def create_app() -> gr.Blocks:
    """
    创建 Gradio Web 应用
    
    Returns:
        Gradio 应用实例
    """
    try:
        logger.info("创建 Gradio Web 应用")
        
        # 初始化日志
        setup_logging()
        
        # 确保必要的目录存在
        ensure_directory(settings.docs_dir_abs)
        ensure_directory(settings.vector_db_dir_abs)
        ensure_directory(settings.model_cache_dir_abs)
        ensure_directory(settings.log_dir_abs)
        
        # 创建应用
        with gr.Blocks(
            title=settings.APP_NAME
        ) as demo:
            
            # 应用标题
            gr.Markdown(f"""
            # {settings.APP_NAME}
            ### {settings.APP_DESCRIPTION}
            *版本: {settings.APP_VERSION} | 基于本地大模型的离线 RAG 系统*
            """)
            
            with gr.Row():
                # 左侧：文档管理区
                with gr.Column(scale=1):
                    gr.Markdown("## 📚 知识库管理")
                    
                    # 文档列表显示
                    gr.Markdown("### 📁 当前文档列表")
                    doc_display = gr.HTML(
                        value=get_html_content(),
                        label="",
                        elem_classes="doc-display"
                    )
                    
                    # 刷新按钮
                    with gr.Row():
                        refresh_btn = gr.Button(
                            "🔄 刷新文档列表", 
                            variant="secondary", 
                            size="sm",
                            scale=1
                        )
                        status_btn = gr.Button(
                            "📊 系统状态", 
                            variant="secondary", 
                            size="sm",
                            scale=1
                        )
                        test_btn = gr.Button(
                            "🧪 测试流程", 
                            variant="secondary", 
                            size="sm",
                            scale=1
                        )
                    
                    refresh_btn.click(
                        refresh_document_list,
                        inputs=None,
                        outputs=doc_display
                    )
                    
                    gr.Markdown("---")
                    
                    # 文档上传和构建
                    gr.Markdown("### 📤 上传文档")
                    upload_files = gr.File(
                        label="上传文档 (PDF/TXT/DOCX)",
                        file_types=[".txt", ".pdf", ".docx"],
                        file_count="multiple",
                        interactive=True
                    )
                    
                    with gr.Row():
                        build_btn = gr.Button(
                            "🚀 一键构建知识库", 
                            variant="primary",
                            scale=1
                        )
                        reload_btn = gr.Button(
                            "🔄 重新加载", 
                            variant="secondary",
                            scale=1
                        )
                    
                    build_info = gr.Textbox(
                        label="构建状态",
                        interactive=False,
                        lines=4,
                        max_lines=10
                    )
                    
                    # 点击构建按钮后更新文档列表
                    build_btn.click(
                        upload_and_build_knowledge,
                        inputs=[upload_files],
                        outputs=[build_info, doc_display]
                    )
                    
                    reload_btn.click(
                        refresh_document_list,
                        inputs=None,
                        outputs=doc_display
                    )
                    
                    # 系统状态面板
                    status_panel = gr.HTML(
                        value="",
                        label="系统状态",
                        visible=False,
                        elem_classes="status-panel"
                    )
                    
                    # 测试结果面板
                    test_panel = gr.JSON(
                        value={},
                        label="测试结果",
                        visible=False
                    )
                    
                    # 状态按钮点击事件
                    def toggle_status_panel():
                        """切换状态面板显示"""
                        status = get_system_status()
                        html = format_status_html(status)
                        return gr.update(value=html, visible=True)
                    
                    status_btn.click(
                        toggle_status_panel,
                        inputs=None,
                        outputs=status_panel
                    )
                    
                    # 测试按钮点击事件
                    def toggle_test_panel():
                        """切换测试面板显示"""
                        test_result = test_rag_pipeline()
                        return gr.update(value=test_result, visible=True)
                    
                    test_btn.click(
                        toggle_test_panel,
                        inputs=None,
                        outputs=test_panel
                    )
                
                # 右侧：对话区
                with gr.Column(scale=2):
                    gr.Markdown("## 💬 智能问答")
                    
                    # 聊天机器人
                    chatbot = gr.Chatbot(
                        height=500,
                        label="对话历史",
                        elem_classes="chatbot"
                    )
                    
                    # 输入框和按钮
                    with gr.Row():
                        msg = gr.Textbox(
                            label="输入问题",
                            placeholder="请基于知识库内容提问...",
                            scale=4,
                            container=False
                        )
                        submit_btn = gr.Button(
                            "发送", 
                            variant="primary",
                            scale=1
                        )
                        clear_btn = gr.Button(
                            "清空", 
                            variant="secondary",
                            scale=1
                        )
                    
                    # 提交对话
                    msg.submit(
                        chat_response,
                        inputs=[msg, chatbot],
                        outputs=[chatbot]
                    )
                    
                    submit_btn.click(
                        chat_response,
                        inputs=[msg, chatbot],
                        outputs=[chatbot]
                    )
                    
                    # 清空对话
                    clear_btn.click(
                        lambda: None,
                        inputs=None,
                        outputs=[chatbot],
                        queue=False
                    )
                    
                    # 使用说明
                    with gr.Accordion("📖 使用说明", open=False):
                        gr.Markdown("""
                        ### 使用指南
                        
                        1. **上传文档**：在左侧上传 PDF、TXT 或 DOCX 格式的文档
                        2. **构建知识库**：点击"一键构建知识库"按钮处理文档并创建向量数据库
                        3. **智能问答**：在右侧输入问题，系统会基于知识库内容回答
                        4. **系统状态**：点击"系统状态"按钮查看当前系统运行状态
                        5. **测试流程**：点击"测试流程"按钮验证 RAG 流程是否正常
                        
                        ### 注意事项
                        - 首次使用需要先上传文档并构建知识库
                        - 支持中文、英文等多种语言的问题
                        - 系统完全离线运行，保护数据隐私
                        - 如果遇到问题，请检查系统状态面板
                        """)
            
            # 页脚
            gr.Markdown(f"""
            ---
            <div style="text-align: center; color: #666; font-size: 0.9em;">
                {settings.APP_NAME} v{settings.APP_VERSION} | 
                服务地址: {settings.WEB_HOST}:{settings.WEB_PORT} | 
                基于 Ollama 本地大模型
            </div>
            """)
        
        logger.info("Gradio Web 应用创建成功")
        return demo
        
    except Exception as e:
        logger.error(f"创建 Gradio Web 应用失败: {e}")
        raise


def launch_app(
    server_name: Optional[str] = None,
    server_port: Optional[int] = None,
    share: Optional[bool] = None,
    debug: Optional[bool] = None
) -> None:
    """
    启动 Web 应用
    
    Args:
        server_name: 服务器主机名
        server_port: 服务器端口
        share: 是否生成公共链接
        debug: 是否启用调试模式
    """
    try:
        # 使用配置值或参数值
        if server_name is None:
            server_name = settings.WEB_HOST
        if server_port is None:
            server_port = settings.WEB_PORT
        if share is None:
            share = settings.WEB_SHARE
        if debug is None:
            debug = settings.WEB_DEBUG
        
        logger.info(f"启动 Web 应用: {server_name}:{server_port}")
        logger.info(f"应用配置: share={share}, debug={debug}")
        
        # 创建并启动应用
        app = create_app()
        app.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            debug=debug,
            inbrowser=True,
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1400px !important;
                margin: 0 auto !important;
            }
            .chatbot {
                min-height: 500px;
            }
            .status-panel {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            """
        )
        
    except Exception as e:
        logger.error(f"启动 Web 应用失败: {e}")
        raise