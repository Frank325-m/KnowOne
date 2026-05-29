"""
向量数据库工具模块
处理向量数据库的创建、加载、检索等操作
支持多种向量数据库：ChromaDB、FAISS、Milvus、Qdrant
使用新的向量数据库架构
"""

import os
import logging
from typing import List, Tuple, Optional, Callable, Union
from pathlib import Path

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from config.settings import settings
from config.logging_config import get_logger
from core.exceptions import (
    VectorDBError,
    RetrievalError,
    NoRelevantDocumentsError,
    EmbeddingError,
    handle_rag_error
)
from core.vector_db.vector_db_factory import get_vector_store
from core.vector_db.base_vector_db import BaseVectorStore

# 获取日志记录器
logger = get_logger(__name__)


@handle_rag_error
def get_embedding_model() -> OllamaEmbeddings:
    """
    获取开源向量模型（本地运行：免费，无需API key）
    使用 Ollama 的嵌入模型
    
    Returns:
        OllamaEmbeddings 实例
        
    Raises:
        EmbeddingError: 如果无法加载嵌入模型
    """
    try:
        logger.info(f"正在加载嵌入模型: {settings.EMBED_MODEL_NAME}")
        
        embedding_model = OllamaEmbeddings(
            model=settings.EMBED_MODEL_NAME,
            temperature=0.0
        )
        
        logger.info(f"嵌入模型加载成功: {settings.EMBED_MODEL_NAME}")
        return embedding_model
        
    except Exception as e:
        logger.error(f"嵌入模型加载失败: {e}")
        raise EmbeddingError(
            model_name=settings.EMBED_MODEL_NAME,
            error=str(e)
        )


@handle_rag_error
def create_vector_store(
    chunk_docs: List[Document],
    persist_dir: Optional[Path] = None,
    collection_name: str = None
) -> BaseVectorStore:
    """
    创建向量数据库
    把切块后的文本-> 向量化 -> 存入向量数据库
    支持多种向量数据库：ChromaDB、FAISS、Milvus、Qdrant
    
    Args:
        chunk_docs: 切块后的文档列表
        persist_dir: 持久化目录（仅对本地数据库有效）
        collection_name: 集合名称
        
    Returns:
        BaseVectorStore 实例
        
    Raises:
        VectorDBError: 如果无法创建向量数据库
    """
    try:
        logger.info(f"正在创建 {settings.VECTOR_DB_TYPE} 向量数据库，文档数量: {len(chunk_docs)}")
        
        # 获取嵌入模型
        embedding_model = get_embedding_model()
        
        # 使用工厂创建向量数据库
        vector_store = get_vector_store(
            engine=settings.VECTOR_DB_TYPE,
            embedding=embedding_model
        )
        
        # 添加文档
        vector_store.add_documents(chunk_docs)
        
        logger.info(f"{settings.VECTOR_DB_TYPE} 向量数据库创建成功")
        
        return vector_store
        
    except Exception as e:
        logger.error(f"向量数据库创建失败: {e}")
        raise VectorDBError(
            message=f"无法创建向量数据库: {str(e)}",
            details={"error": str(e)}
        )


@handle_rag_error
def load_existing_vector_store(
    persist_dir: Optional[Path] = None,
    collection_name: str = None
) -> BaseVectorStore:
    """
    加载已存在的向量数据库
    
    Args:
        persist_dir: 持久化目录（仅对本地数据库有效）
        collection_name: 集合名称
        
    Returns:
        BaseVectorStore 实例
        
    Raises:
        VectorDBError: 如果无法加载向量数据库
    """
    try:
        logger.info(f"正在加载 {settings.VECTOR_DB_TYPE} 向量数据库")
        
        # 获取嵌入模型
        embedding_model = get_embedding_model()
        
        # 使用工厂加载向量数据库
        vector_store = get_vector_store(
            engine=settings.VECTOR_DB_TYPE,
            embedding=embedding_model
        )
        
        logger.info(f"{settings.VECTOR_DB_TYPE} 向量数据库加载成功")
        
        return vector_store
        
    except Exception as e:
        logger.error(f"向量数据库加载失败: {e}")
        raise VectorDBError(
            message=f"无法加载向量数据库: {str(e)}",
            details={"error": str(e)}
        )


@handle_rag_error
def search_knowledge(
    query: str,
    top_k: int = None
) -> Tuple[str, List[Document]]:
    """
    传入问题，返回匹配到的知识库原文
    
    Args:
        query: 检索问题
        top_k: 检索结果数量
        
    Returns:
        tuple: (上下文文本, 文档列表)
        
    Raises:
        RetrievalError: 如果检索失败
        NoRelevantDocumentsError: 如果未找到相关文档
    """
    try:
        if not query or not query.strip():
            logger.warning("检索查询为空")
            raise RetrievalError("检索查询不能为空", query=query)
        
        logger.info(f"开始检索: '{query}'")
        
        # 使用配置值或参数值
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        # 加载向量数据库
        vector_store = load_existing_vector_store()
        
        # 执行检索
        docs = vector_store.search(query, top_k=top_k)
        
        if not docs:
            logger.warning(f"未找到相关文档: '{query}'")
            raise NoRelevantDocumentsError(
                query=query,
                top_k=top_k
            )
        
        # 拼接检索到的上下文
        context = "\n\n".join([doc.page_content for doc in docs])
        
        logger.info(f"检索成功，找到 {len(docs)} 个相关文档")
        logger.debug(f"检索上下文长度: {len(context)} 字符")
        
        return context, docs
        
    except NoRelevantDocumentsError as e:
        raise e
    except Exception as e:
        logger.error(f"检索失败: {e}")
        raise RetrievalError(
            message="知识检索失败",
            query=query,
            details={"error": str(e)}
        )


@handle_rag_error
def manual_search_query(
    query: str,
    top_k: int = None
) -> Tuple[str, List[Document]]:
    """
    手动检索（直接向量化查询）
    
    Args:
        query: 检索问题
        top_k: 检索结果数量
        
    Returns:
        tuple: (上下文文本, 文档列表)
        
    Raises:
        RetrievalError: 如果检索失败
    """
    try:
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        logger.info(f"开始手动检索: '{query}' (top_k={top_k})")
        
        # 直接使用 search 方法
        return search_knowledge(query, top_k=top_k)
        
    except Exception as e:
        logger.error(f"手动检索失败: {e}")
        raise RetrievalError(
            message="手动检索失败",
            query=query,
            details={"error": str(e)}
        )


@handle_rag_error
def search_with_rerank(
    query: str,
    top_k: int = None
) -> Tuple[str, List[Document]]:
    """
    带重排的检索接口
    
    Args:
        query: 检索问题
        top_k: 检索结果数量
        
    Returns:
        tuple: (上下文文本, 文档列表)
        
    Raises:
        RetrievalError: 如果检索失败
        NoRelevantDocumentsError: 如果未找到相关文档
    """
    try:
        logger.info(f"开始带重排检索: '{query}'")
        
        # 使用配置值或参数值
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        
        # 加载向量数据库
        vector_store = load_existing_vector_store()
        
        # 获取更多文档用于重排
        fetch_k = settings.FETCH_K if hasattr(settings, 'FETCH_K') else top_k * 2
        docs = vector_store.search(query, top_k=fetch_k)
        
        if not docs:
            logger.warning(f"重排检索未找到原始文档: '{query}'")
            raise NoRelevantDocumentsError(
                query=query,
                top_k=top_k
            )
        
        # 本地轻量化过滤，按字符长度+关键词简单过滤
        def filter_docs(docs: List[Document], query: str) -> List[Document]:
            """过滤文档列表"""
            if not docs:
                return []
            
            logger.debug(f"开始文档过滤，原始文档数: {len(docs)}")
            
            filter_docs = []
            q_words = set(query)
            
            for doc in docs:
                # 过滤过短无效文本
                if len(doc.page_content) < 50:
                    logger.debug(f"过滤过短文档: {len(doc.page_content)} 字符")
                    continue
                
                # 粗略匹配关键词
                match_cnt = sum(1 for w in q_words if w in doc.page_content)
                if match_cnt > 0:
                    filter_docs.append(doc)
            
            # 限制返回数量
            result = filter_docs[:top_k]
            logger.debug(f"文档过滤完成，过滤后文档数: {len(result)}")
            
            return result
        
        # 执行过滤
        final_docs = filter_docs(docs, query)
        
        if not final_docs:
            logger.warning(f"重排后无有效文档: '{query}'")
            raise NoRelevantDocumentsError(
                query=query,
                top_k=top_k
            )
        
        # 拼接检索到的上下文
        context = "\n\n".join([doc.page_content for doc in final_docs])
        
        logger.info(f"带重排检索成功，原始文档: {len(docs)}，重排后: {len(final_docs)}")
        
        return context, final_docs
        
    except NoRelevantDocumentsError as e:
        raise e
    except Exception as e:
        logger.error(f"带重排检索失败: {e}")
        raise RetrievalError(
            message="带重排检索失败",
            query=query,
            details={"error": str(e)}
        )


@handle_rag_error
def get_vector_store_info() -> dict:
    """
    获取向量数据库信息
    
    Returns:
        向量数据库信息字典
        
    Raises:
        VectorDBError: 如果无法获取信息
    """
    try:
        # 尝试加载向量数据库以获取更多信息
        document_count = 0
        try:
            vector_store = load_existing_vector_store()
            document_count = vector_store.get_document_count()
        except:
            pass
        
        # 返回基本信息
        info = {
            "db_type": settings.VECTOR_DB_TYPE,
            "docs_dir": str(settings.DOCS_DIR),
            "vector_db_dir": str(settings.get_vector_db_dir()),
            "embedding_model": settings.EMBED_MODEL_NAME,
            "document_count": document_count
        }
        
        logger.debug(f"向量数据库信息: {info}")
        return info
        
    except Exception as e:
        logger.error(f"获取向量数据库信息失败: {e}")
        raise VectorDBError(
            message="无法获取向量数据库信息",
            details={"error": str(e)}
        )