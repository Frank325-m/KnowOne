from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from core.vector_db.base_vector_db import BaseVectorStore

class FAISSStore(BaseVectorStore):
    def __init__(self, embedding, persist_dir="./resource/vector_db/faiss_db"):
        self.embedding = embedding
        self.persist_dir = persist_dir
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
        import os
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
        self.db = None