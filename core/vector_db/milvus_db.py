from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Milvus
from core.vector_db.base_vector_db import BaseVectorStore
from config.settings import settings

class MilvusStore(BaseVectorStore):
    def __init__(self, embedding, persist_dir=None):
        super().__init__(embedding)
        self.persist_dir = persist_dir or str(settings.get_vector_db_dir("milvus"))
        self.db = None
        self.collection_name = settings.VECTOR_DB_COLLECTION
        self.connection_args = {
            "host": settings.MILVUS_HOST,
            "port": settings.MILVUS_PORT,
            "user": settings.MILVUS_USER,
            "password": settings.MILVUS_PASSWORD
        }
        
        # 过滤空值
        self.connection_args = {k: v for k, v in self.connection_args.items() if v}
    
    def add_documents(self, documents: List[Document]) -> None:
        if self.db is None:
            self.db = Milvus.from_documents(
                documents=documents,
                embedding=self.embedding,
                connection_args=self.connection_args,
                collection_name=self.collection_name
            )
        else:
            self.db.add_documents(documents)
    
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        if self.db is None:
            return []
        return self.db.similarity_search(query, k=top_k)
    
    def clear(self) -> None:
        # Milvus是远程数据库，需要删除集合而不是本地目录
        if self.db is not None:
            try:
                # 尝试删除集合
                if hasattr(self.db, 'col'):
                    self.db.col.drop()
            except Exception as e:
                print(f"警告: 无法删除Milvus集合: {e}")
        self.db = None
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        if self.db is None:
            return 0
        try:
            if hasattr(self.db, 'col'):
                return self.db.col.num_entities
            return 0
        except:
            return 0