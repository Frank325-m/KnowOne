from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Qdrant
from core.vector_db.base_vector_db import BaseVectorStore
from config.settings import settings

class QdrantStore(BaseVectorStore):
    def __init__(self, embedding, persist_dir=None):
        super().__init__(embedding)
        self.persist_dir = persist_dir or str(settings.get_vector_db_dir("qdrant"))
        self.db = None
        self.collection_name = settings.VECTOR_DB_COLLECTION
        self.url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}"
        self.api_key = settings.QDRANT_API_KEY
        self.prefer_grpc = settings.QDRANT_PREFER_GRPC
    
    def add_documents(self, documents: List[Document]) -> None:
        if self.db is None:
            self.db = Qdrant.from_documents(
                documents=documents,
                embedding=self.embedding,
                url=self.url,
                api_key=self.api_key if self.api_key else None,
                prefer_grpc=self.prefer_grpc,
                collection_name=self.collection_name
            )
        else:
            self.db.add_documents(documents)
    
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        if self.db is None:
            return []
        return self.db.similarity_search(query, k=top_k)
    
    def clear(self) -> None:
        # Qdrant是远程数据库，需要删除集合而不是本地目录
        if self.db is not None:
            try:
                # 尝试删除集合
                if hasattr(self.db, 'client'):
                    self.db.client.delete_collection(self.collection_name)
            except Exception as e:
                print(f"警告: 无法删除Qdrant集合: {e}")
        self.db = None
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        if self.db is None:
            return 0
        try:
            if hasattr(self.db, 'client'):
                collection_info = self.db.client.get_collection(self.collection_name)
                return collection_info.points_count
            return 0
        except:
            return 0