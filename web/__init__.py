"""
Web 应用模块
提供基于 Gradio 的 RAG 知识库问答系统 Web 界面
"""

from .app import (
    create_app,
    get_html_content,
    upload_and_build_knowledge,
    chat_response,
    refresh_document_list,
    get_system_status,
    get_vector_db_info,
    test_rag_pipeline
)

__all__ = [
    'create_app',
    'get_html_content',
    'upload_and_build_knowledge',
    'chat_response',
    'refresh_document_list',
    'get_system_status',
    'get_vector_db_info',
    'test_rag_pipeline'
]