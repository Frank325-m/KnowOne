from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Milvus
from core.vector_db.base_vector_db import BaseVectorStore

class MilvusStore(BaseVectorStore):
    def __init__(self, embedding, persist_dir="./resource/vector_db/milvus_db"):
        super().__init__(embedding)
        self.persist_dir = persist_dir
        self.db = None
    
    def add_documents(self, documents: List[Document]) -> None:
        if self.db is None:
            self.db = Milvus.from_documents(
                documents=documents,
                embedding=self.embedding,
                connection_args={"host": "localhost", "port": "19530"},
                collection_name="knowledge_base"
            )
        else:
            self.db.add_documents(documents)
    
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