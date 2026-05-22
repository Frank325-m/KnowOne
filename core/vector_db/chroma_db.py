from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from core.vector_db.base_vector_db import BaseVectorStore

class ChromaStore(BaseVectorStore):
    def __init__(self, embedding, persist_dir="./resource/vector_db/chroma_db"):
        super().__init__(embedding)
        self.persist_dir = persist_dir
        self.db = None
    
    def add_documents(self, documents: List[Document]) -> None:
        if self.db is None:
            self.db = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding,
                persist_directory=self.persist_dir
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
        import time
        
        # 先关闭数据库连接
        if self.db is not None:
            try:
                # ChromaDB 没有显式的关闭方法，设置为 None 让垃圾回收处理
                self.db = None
            except:
                pass
        
        # 尝试删除目录，如果失败则忽略
        if os.path.exists(self.persist_dir):
            try:
                # 等待一小段时间让文件释放
                time.sleep(0.1)
                shutil.rmtree(self.persist_dir)
            except (PermissionError, OSError) as e:
                print(f"警告: 无法删除目录 {self.persist_dir}: {e}")
                # 尝试重命名目录而不是删除
                try:
                    timestamp = int(time.time())
                    new_name = f"{self.persist_dir}_deleted_{timestamp}"
                    os.rename(self.persist_dir, new_name)
                    print(f"已将目录重命名为: {new_name}")
                except:
                    pass