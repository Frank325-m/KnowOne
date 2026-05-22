"""
向量数据库工厂模块
支持多种向量数据库的无缝切换：ChromaDB、FAISS、Milvus、Qdrant
"""

import os
import logging
from typing import List, Optional, Union, Dict, Any
from pathlib import Path
from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from langchain_milvus import Milvus
from langchain_qdrant import Qdrant

from config.settings import settings
from config.logging_config import get_logger
from core.exceptions import (
    VectorDBError,
    VectorDBNotFoundError,
    VectorDBCreationError,
    VectorDBQueryError
)

# 获取日志记录器
logger = get_logger(__name__)


class VectorStoreFactory:
    """向量数据库工厂类"""
    
    @staticmethod
    def create_vector_store(
        documents: List[Document],
        embedding: Embeddings,
        collection_name: Optional[str] = None,
        **kwargs
    ) -> VectorStore:
        """
        创建向量数据库
        
        Args:
            documents: 文档列表
            embedding: 嵌入模型
            collection_name: 集合名称
            **kwargs: 额外参数
            
        Returns:
            VectorStore 实例
            
        Raises:
            VectorDBCreationError: 如果无法创建向量数据库
        """
        try:
            if collection_name is None:
                collection_name = settings.VECTOR_DB_COLLECTION
            
            db_type = settings.VECTOR_DB_TYPE.lower()
            logger.info(f"正在创建 {db_type} 向量数据库，文档数量: {len(documents)}")
            
            if db_type == "chroma":
                return VectorStoreFactory._create_chroma(
                    documents, embedding, collection_name, **kwargs
                )
            elif db_type == "faiss":
                return VectorStoreFactory._create_faiss(
                    documents, embedding, collection_name, **kwargs
                )
            elif db_type == "milvus":
                return VectorStoreFactory._create_milvus(
                    documents, embedding, collection_name, **kwargs
                )
            elif db_type == "qdrant":
                return VectorStoreFactory._create_qdrant(
                    documents, embedding, collection_name, **kwargs
                )
            else:
                raise VectorDBCreationError(
                    db_path="",
                    error=f"不支持的向量数据库类型: {db_type}"
                )
                
        except Exception as e:
            logger.error(f"向量数据库创建失败: {e}")
            raise VectorDBCreationError(
                db_path=VectorStoreFactory._get_db_path(),
                error=str(e)
            )
    
    @staticmethod
    def load_vector_store(
        embedding: Embeddings,
        collection_name: Optional[str] = None,
        **kwargs
    ) -> VectorStore:
        """
        加载已存在的向量数据库
        
        Args:
            embedding: 嵌入模型
            collection_name: 集合名称
            **kwargs: 额外参数
            
        Returns:
            VectorStore 实例
            
        Raises:
            VectorDBNotFoundError: 如果向量数据库不存在
            VectorDBError: 如果无法加载向量数据库
        """
        try:
            if collection_name is None:
                collection_name = settings.VECTOR_DB_COLLECTION
            
            db_type = settings.VECTOR_DB_TYPE.lower()
            logger.info(f"正在加载 {db_type} 向量数据库")
            
            if db_type == "chroma":
                return VectorStoreFactory._load_chroma(
                    embedding, collection_name, **kwargs
                )
            elif db_type == "faiss":
                return VectorStoreFactory._load_faiss(
                    embedding, collection_name, **kwargs
                )
            elif db_type == "milvus":
                return VectorStoreFactory._load_milvus(
                    embedding, collection_name, **kwargs
                )
            elif db_type == "qdrant":
                return VectorStoreFactory._load_qdrant(
                    embedding, collection_name, **kwargs
                )
            else:
                raise VectorDBNotFoundError(
                    db_path=VectorStoreFactory._get_db_path()
                )
                
        except VectorDBNotFoundError as e:
            raise e
        except Exception as e:
            logger.error(f"向量数据库加载失败: {e}")
            raise VectorDBError(
                message="无法加载向量数据库",
                db_path=VectorStoreFactory._get_db_path(),
                details={"error": str(e)}
            )
    
    @staticmethod
    def get_vector_store_info() -> Dict[str, Any]:
        """
        获取向量数据库信息
        
        Returns:
            向量数据库信息字典
        """
        try:
            db_type = settings.VECTOR_DB_TYPE.lower()
            
            if db_type == "chroma":
                return VectorStoreFactory._get_chroma_info()
            elif db_type == "faiss":
                return VectorStoreFactory._get_faiss_info()
            elif db_type == "milvus":
                return VectorStoreFactory._get_milvus_info()
            elif db_type == "qdrant":
                return VectorStoreFactory._get_qdrant_info()
            else:
                return {
                    "exists": False,
                    "db_type": db_type,
                    "message": f"不支持的向量数据库类型: {db_type}"
                }
                
        except Exception as e:
            logger.error(f"获取向量数据库信息失败: {e}")
            return {
                "exists": False,
                "db_type": db_type,
                "message": f"获取信息失败: {str(e)}"
            }
    
    @staticmethod
    def _get_db_path() -> str:
        """获取数据库路径"""
        if settings.VECTOR_DB_TYPE.lower() == "chroma":
            return str(settings.vector_db_dir_abs)
        elif settings.VECTOR_DB_TYPE.lower() == "faiss":
            return str(settings.vector_db_dir_abs / "faiss_index")
        else:
            return f"{settings.VECTOR_DB_TYPE}:{settings.VECTOR_DB_COLLECTION}"
    
    # ============ ChromaDB 方法 ============
    
    @staticmethod
    def _create_chroma(
        documents: List[Document],
        embedding: Embeddings,
        collection_name: str,
        **kwargs
    ) -> Chroma:
        """创建 ChromaDB 向量数据库"""
        persist_dir = settings.vector_db_dir_abs
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        return Chroma.from_documents(
            documents=documents,
            embedding=embedding,
            persist_directory=str(persist_dir),
            collection_name=collection_name,
            **kwargs
        )
    
    @staticmethod
    def _load_chroma(
        embedding: Embeddings,
        collection_name: str,
        **kwargs
    ) -> Chroma:
        """加载 ChromaDB 向量数据库"""
        persist_dir = settings.vector_db_dir_abs
        
        if not persist_dir.exists():
            raise VectorDBNotFoundError(db_path=str(persist_dir))
        
        if not any(persist_dir.iterdir()):
            raise VectorDBNotFoundError(db_path=str(persist_dir))
        
        return Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embedding,
            collection_name=collection_name,
            **kwargs
        )
    
    @staticmethod
    def _get_chroma_info() -> Dict[str, Any]:
        """获取 ChromaDB 信息"""
        try:
            from langchain_ollama import OllamaEmbeddings
            embedding = OllamaEmbeddings(model=settings.EMBED_MODEL_NAME)
            vector_store = VectorStoreFactory._load_chroma(embedding, settings.VECTOR_DB_COLLECTION)
            collection = vector_store._collection
            
            return {
                "exists": True,
                "db_type": "chroma",
                "collection_name": collection.name,
                "document_count": collection.count(),
                "metadata": collection.metadata,
                "persist_directory": str(settings.vector_db_dir_abs),
                "embedding_model": settings.EMBED_MODEL_NAME
            }
        except VectorDBNotFoundError:
            return {
                "exists": False,
                "db_type": "chroma",
                "persist_directory": str(settings.vector_db_dir_abs),
                "message": "向量数据库不存在"
            }
    
    # ============ FAISS 方法 ============
    
    @staticmethod
    def _create_faiss(
        documents: List[Document],
        embedding: Embeddings,
        collection_name: str,
        **kwargs
    ) -> FAISS:
        """创建 FAISS 向量数据库"""
        index_path = settings.vector_db_dir_abs / "faiss_index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embedding,
            **kwargs
        )
        
        if settings.VECTOR_DB_PERSIST:
            vector_store.save_local(str(index_path))
        
        return vector_store
    
    @staticmethod
    def _load_faiss(
        embedding: Embeddings,
        collection_name: str,
        **kwargs
    ) -> FAISS:
        """加载 FAISS 向量数据库"""
        index_path = settings.vector_db_dir_abs / "faiss_index"
        
        if not index_path.exists():
            raise VectorDBNotFoundError(db_path=str(index_path))
        
        return FAISS.load_local(
            str(index_path),
            embedding,
            allow_dangerous_deserialization=True,
            **kwargs
        )
    
    @staticmethod
    def _get_faiss_info() -> Dict[str, Any]:
        """获取 FAISS 信息"""
        try:
            from langchain_ollama import OllamaEmbeddings
            embedding = OllamaEmbeddings(model=settings.EMBED_MODEL_NAME)
            vector_store = VectorStoreFactory._load_faiss(embedding, settings.VECTOR_DB_COLLECTION)
            
            return {
                "exists": True,
                "db_type": "faiss",
                "document_count": vector_store.index.ntotal,
                "index_path": str(settings.vector_db_dir_abs / "faiss_index"),
                "embedding_model": settings.EMBED_MODEL_NAME,
                "dimension": vector_store.index.d
            }
        except VectorDBNotFoundError:
            return {
                "exists": False,
                "db_type": "faiss",
                "index_path": str(settings.vector_db_dir_abs / "faiss_index"),
                "message": "向量数据库不存在"
            }
    
    # ============ Milvus 方法 ============
    
    @staticmethod
    def _create_milvus(
        documents: List[Document],
        embedding: Embeddings,
        collection_name: str,
        **kwargs
    ) -> Milvus:
        """创建 Milvus 向量数据库"""
        connection_args = {
            "host": settings.MILVUS_HOST,
            "port": settings.MILVUS_PORT,
        }
        
        if settings.MILVUS_USER and settings.MILVUS_PASSWORD:
            connection_args.update({
                "user": settings.MILVUS_USER,
                "password": settings.MILVUS_PASSWORD
            })
        
        return Milvus.from_documents(
            documents=documents,
            embedding=embedding,
            collection_name=collection_name,
            connection_args=connection_args,
            **kwargs
        )
    
    @staticmethod
    def _load_milvus(
        embedding: Embeddings,
        collection_name: str,
        **kwargs
    ) -> Milvus:
        """加载 Milvus 向量数据库"""
        connection_args = {
            "host": settings.MILVUS_HOST,
            "port": settings.MILVUS_PORT,
        }
        
        if settings.MILVUS_USER and settings.MILVUS_PASSWORD:
            connection_args.update({
                "user": settings.MILVUS_USER,
                "password": settings.MILVUS_PASSWORD
            })
        
        return Milvus(
            embedding_function=embedding,
            collection_name=collection_name,
            connection_args=connection_args,
            **kwargs
        )
    
    @staticmethod
    def _get_milvus_info() -> Dict[str, Any]:
        """获取 Milvus 信息"""
        try:
            from pymilvus import connections, utility
            
            connection_args = {
                "host": settings.MILVUS_HOST,
                "port": settings.MILVUS_PORT,
            }
            
            if settings.MILVUS_USER and settings.MILVUS_PASSWORD:
                connection_args.update({
                    "user": settings.MILVUS_USER,
                    "password": settings.MILVUS_PASSWORD
                })
            
            connections.connect(**connection_args)
            
            if utility.has_collection(settings.VECTOR_DB_COLLECTION):
                collection = utility.get_collection_stats(settings.VECTOR_DB_COLLECTION)
                return {
                    "exists": True,
                    "db_type": "milvus",
                    "collection_name": settings.VECTOR_DB_COLLECTION,
                    "document_count": collection["row_count"],
                    "host": settings.MILVUS_HOST,
                    "port": settings.MILVUS_PORT,
                    "embedding_model": settings.EMBED_MODEL_NAME
                }
            else:
                return {
                    "exists": False,
                    "db_type": "milvus",
                    "collection_name": settings.VECTOR_DB_COLLECTION,
                    "message": "集合不存在"
                }
                
        except Exception as e:
            return {
                "exists": False,
                "db_type": "milvus",
                "collection_name": settings.VECTOR_DB_COLLECTION,
                "message": f"连接失败: {str(e)}"
            }
    
    # ============ Qdrant 方法 ============
    
    @staticmethod
    def _create_qdrant(
        documents: List[Document],
        embedding: Embeddings,
        collection_name: str,
        **kwargs
    ) -> Qdrant:
        """创建 Qdrant 向量数据库"""
        from qdrant_client import QdrantClient
        from qdrant_client.http import models as qdrant_models
        
        client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
            prefer_grpc=settings.QDRANT_PREFER_GRPC,
            **kwargs.get("client_kwargs", {})
        )
        
        return Qdrant.from_documents(
            documents=documents,
            embedding=embedding,
            collection_name=collection_name,
            client=client,
            **kwargs
        )
    
    @staticmethod
    def _load_qdrant(
        embedding: Embeddings,
        collection_name: str,
        **kwargs
    ) -> Qdrant:
        """加载 Qdrant 向量数据库"""
        from qdrant_client import QdrantClient
        
        client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
            prefer_grpc=settings.QDRANT_PREFER_GRPC,
            **kwargs.get("client_kwargs", {})
        )
        
        return Qdrant(
            client=client,
            collection_name=collection_name,
            embeddings=embedding,
            **kwargs
        )
    
    @staticmethod
    def _get_qdrant_info() -> Dict[str, Any]:
        """获取 Qdrant 信息"""
        try:
            from qdrant_client import QdrantClient
            
            client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                prefer_grpc=settings.QDRANT_PREFER_GRPC
            )
            
            collections = client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            exists = settings.VECTOR_DB_COLLECTION in collection_names
            
            if exists:
                collection_info = client.get_collection(settings.VECTOR_DB_COLLECTION)
                return {
                    "exists": True,
                    "db_type": "qdrant",
                    "collection_name": settings.VECTOR_DB_COLLECTION,
                    "vectors_count": collection_info.vectors_count,
                    "host": settings.QDRANT_HOST,
                    "port": settings.QDRANT_PORT,
                    "embedding_model": settings.EMBED_MODEL_NAME
                }
            else:
                return {
                    "exists": False,
                    "db_type": "qdrant",
                    "collection_name": settings.VECTOR_DB_COLLECTION,
                    "message": "集合不存在"
                }
                
        except Exception as e:
            return {
                "exists": False,
                "db_type": "qdrant",
                "collection_name": settings.VECTOR_DB_COLLECTION,
                "message": f"连接失败: {str(e)}"
            }