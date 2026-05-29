from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from core.vector_db.base_vector_db import BaseVectorStore
from config.settings import settings
import os

class FAISSStore(BaseVectorStore):
    def __init__(self, embedding, persist_dir=None):
        super().__init__(embedding)
        self.persist_dir = persist_dir or str(settings.get_vector_db_dir("faiss"))
        self.db = None
        
        # 尝试加载已存在的数据库
        if os.path.exists(self.persist_dir):
            try:
                self.db = FAISS.load_local(
                    self.persist_dir,
                    self.embedding,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"警告: 无法加载已存在的FAISS数据库: {e}")
                self.db = None
    
    def add_documents(self, documents: List[Document]) -> None:
        if self.db is None:
            self.db = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding
            )
        else:
            self.db.add_documents(documents)
        self.db.save_local(self.persist_dir)
    
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        if self.db is None:
            return []
        return self.db.similarity_search(query, k=top_k)
    
    def clear(self) -> None:
        import shutil
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
        self.db = None
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        if self.db is None:
            return 0
        try:
            return self.db.index.ntotal
        except:
            return 0