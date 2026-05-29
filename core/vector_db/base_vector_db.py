from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

class BaseVectorStore(ABC):
    def __init__(self, embedding: Embeddings):
        self.embedding = embedding
    
    @abstractmethod
    def add_documents(self, docs: List[Document]) -> None:
        """添加文档到向量数据库"""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        """语义检索"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空库"""
        pass
    
    @abstractmethod
    def get_document_count(self) -> int:
        """获取文档数量"""
        pass