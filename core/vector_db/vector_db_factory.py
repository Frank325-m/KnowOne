from typing import Optional
from langchain_core.embeddings import Embeddings
from core.vector_db.base_vector_db import BaseVectorStore

# 获取向量数据库实例
def get_vector_store(
    engine: str = "faiss",
    embedding: Optional[Embeddings] = None
) -> BaseVectorStore:
    """
    获取指定类型的向量数据库实例
    :param engine: 向量数据库引擎类型，可选值："chroma", "faiss", "milvus", "qdrant"
    :param embedding: 用于向量化的嵌入模型
    :return: 对应的向量数据库实例
    """

    if not embedding:
        raise ValueError("必须传入embedding嵌入模型")

    engine = engine.lower().strip()

    if engine == "chroma":
        from core.vector_db.chroma_db import ChromaStore
        return ChromaStore(embedding=embedding)
    elif engine == "faiss":
        from core.vector_db.faiss_db import FAISSStore
        return FAISSStore(embedding=embedding)
    elif engine == "milvus":
        from core.vector_db.milvus_db import MilvusStore
        return MilvusStore(embedding=embedding)
    elif engine == "qdrant":
        from core.vector_db.qdrant_db import QdrantStore
        return QdrantStore(embedding=embedding)
    else:
        raise ValueError(f"不支持的向量数据库引擎类型: {engine}")
