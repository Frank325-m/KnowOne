# 向量数据库快速使用指南

## 概述

本文档提供新的向量数据库架构的快速使用指南，帮助开发者快速上手。

## 安装依赖

确保已安装所有必要的依赖：

```bash
# 安装核心依赖
pip install -r requirements.txt

# 如果需要特定数据库支持
pip install faiss-cpu          # FAISS 支持
pip install pymilvus           # Milvus 支持
pip install qdrant-client      # Qdrant 支持
```

## 快速开始

### 1. 基本使用

```python
from langchain_ollama import OllamaEmbeddings
from core.vector_db.vector_db_factory import get_vector_store
from langchain_core.documents import Document

# 1. 创建嵌入模型
embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")

# 2. 创建向量数据库实例
# 使用 ChromaDB (默认)
vector_store = get_vector_store(engine="chroma", embedding=embedding)

# 使用 FAISS
# vector_store = get_vector_store(engine="faiss", embedding=embedding)

# 使用 Milvus (需要运行 Milvus 服务)
# vector_store = get_vector_store(engine="milvus", embedding=embedding)

# 使用 Qdrant (需要运行 Qdrant 服务)
# vector_store = get_vector_store(engine="qdrant", embedding=embedding)

# 3. 添加文档
documents = [
    Document(
        page_content="人工智能是当前科技发展的重要方向。",
        metadata={"source": "guide", "category": "科技"}
    ),
    Document(
        page_content="机器学习是人工智能的核心技术之一。",
        metadata={"source": "guide", "category": "技术"}
    ),
    Document(
        page_content="深度学习在图像识别和自然语言处理中广泛应用。",
        metadata={"source": "guide", "category": "应用"}
    )
]

vector_store.add_documents(documents)
print("文档添加成功！")

# 4. 检索文档
query = "人工智能"
results = vector_store.search(query, top_k=2)

print(f"查询: {query}")
for i, doc in enumerate(results):
    print(f"结果 {i+1}: {doc.page_content[:50]}...")
    print(f"元数据: {doc.metadata}")
    print()

# 5. 清空数据库 (可选)
# vector_store.clear()
```

### 2. 配置驱动使用

通过环境变量配置数据库类型：

```python
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from core.vector_db.vector_db_factory import get_vector_store

# 加载环境变量
load_dotenv()

# 从环境变量获取配置
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")

# 创建向量数据库
embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
vector_store = get_vector_store(engine=VECTOR_DB_TYPE, embedding=embedding)

print(f"使用 {VECTOR_DB_TYPE.upper()} 向量数据库")
```

### 3. 高级功能

#### 批量操作

```python
# 批量添加大量文档
large_documents = [
    Document(page_content=f"文档内容 {i}", metadata={"id": i})
    for i in range(1000)
]

# 分批添加以避免内存问题
batch_size = 100
for i in range(0, len(large_documents), batch_size):
    batch = large_documents[i:i + batch_size]
    vector_store.add_documents(batch)
    print(f"已添加 {i + len(batch)}/{len(large_documents)} 个文档")
```

#### 自定义检索

```python
# 自定义检索参数
results = vector_store.search(
    query="技术发展",
    top_k=5  # 返回前5个结果
)

# 处理检索结果
for doc in results:
    # 计算相似度分数 (如果数据库支持)
    # 注意：不是所有数据库都直接返回分数
    print(f"内容: {doc.page_content}")
    print(f"元数据: {doc.metadata}")
    print("-" * 50)
```

## 数据库特定配置

### ChromaDB

```python
from core.vector_db.chroma_db import ChromaStore

# 自定义配置
chroma_store = ChromaStore(
    embedding=embedding,
    persist_dir="./data/chroma_custom"  # 自定义存储目录
)
```

### FAISS

```python
from core.vector_db.faiss_db import FAISSStore

# 自定义配置
faiss_store = FAISSStore(
    embedding=embedding,
    persist_dir="./data/faiss_custom"  # 自定义存储目录
)
```

### Milvus

```python
from core.vector_db.milvus_db import MilvusStore

# 自定义配置
milvus_store = MilvusStore(
    embedding=embedding,
    persist_dir="./data/milvus_custom"  # 自定义存储目录
)

# Milvus 需要额外的连接配置
# 确保 Milvus 服务正在运行
# docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest
```

### Qdrant

```python
from core.vector_db.qdrant_db import QdrantStore

# 自定义配置
qdrant_store = QdrantStore(
    embedding=embedding,
    persist_dir="./data/qdrant_custom"  # 自定义存储目录
)

# Qdrant 需要额外的连接配置
# 确保 Qdrant 服务正在运行
# docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

## 错误处理

### 基本错误处理

```python
try:
    vector_store = get_vector_store(engine="chroma", embedding=embedding)
    results = vector_store.search("查询", top_k=3)
except ValueError as e:
    print(f"配置错误: {e}")
except ConnectionError as e:
    print(f"连接错误: {e}")
    print("请确保数据库服务正在运行")
except Exception as e:
    print(f"未知错误: {e}")
    import traceback
    traceback.print_exc()
```

### 资源清理

```python
import atexit

# 注册清理函数
def cleanup():
    try:
        vector_store.clear()
        print("向量数据库已清理")
    except Exception as e:
        print(f"清理时出错: {e}")

atexit.register(cleanup)
```

## 性能优化

### 1. 批量操作

```python
# 使用批量操作提高性能
documents = load_large_documents()  # 加载大量文档

# 不好的做法：逐个添加
# for doc in documents:
#     vector_store.add_documents([doc])

# 好的做法：批量添加
vector_store.add_documents(documents)
```

### 2. 合理设置 top_k

```python
# 根据需求设置合适的 top_k 值
# 太小的 top_k 可能错过相关文档
# 太大的 top_k 影响性能

# 对于精确检索
precise_results = vector_store.search(query, top_k=3)

# 对于广泛检索
broad_results = vector_store.search(query, top_k=10)
```

### 3. 缓存机制

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(query: str, top_k: int = 3):
    """带缓存的搜索"""
    return vector_store.search(query, top_k=top_k)

# 使用缓存搜索
results = cached_search("常见问题", top_k=5)
```

## 集成到现有项目

### 1. 替换旧代码

```python
# 旧代码 (V1 架构)
from core.vector_factory import VectorStoreFactory

vector_store = VectorStoreFactory.create_vector_store(
    documents=documents,
    embedding=embedding
)

# 新代码 (V2 架构)
from core.vector_db.vector_db_factory import get_vector_store

vector_store = get_vector_store(engine="chroma", embedding=embedding)
vector_store.add_documents(documents)
```

### 2. 保持向后兼容

```python
# 如果需要保持完全兼容，可以使用包装器
from core.vector_db.vector_db_factory import get_vector_store

class VectorStoreWrapper:
    """向后兼容的包装器"""
    
    def __init__(self, embedding, engine="chroma"):
        self.store = get_vector_store(engine=engine, embedding=embedding)
    
    def add_documents(self, documents):
        self.store.add_documents(documents)
    
    def similarity_search(self, query, k=3):
        return self.store.search(query, top_k=k)
    
    def clear(self):
        self.store.clear()

# 使用方式与旧代码相同
vector_store = VectorStoreWrapper(embedding=embedding)
vector_store.add_documents(documents)
results = vector_store.similarity_search("查询", k=3)
```

## 常见问题

### Q1: 如何选择数据库类型？

- **开发/测试环境**: 使用 ChromaDB (轻量级，无需额外服务)
- **生产环境小规模**: 使用 FAISS (高性能，本地运行)
- **生产环境大规模**: 使用 Milvus 或 Qdrant (分布式，云原生)

### Q2: 数据库服务无法连接怎么办？

```bash
# 检查服务状态
# ChromaDB: 无需额外服务
# FAISS: 无需额外服务

# Milvus
docker ps | grep milvus

# Qdrant  
docker ps | grep qdrant

# 启动服务
# Milvus
docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest

# Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### Q3: 如何迁移现有数据？

```python
# 从旧数据库导出
old_store = load_old_vector_store()
old_docs = old_store.get_all_documents()

# 导入到新数据库
new_store = get_vector_store(engine="chroma", embedding=embedding)
new_store.add_documents(old_docs)
```

### Q4: 性能调优建议

1. **调整分块大小**: 文档分块大小影响检索质量
2. **使用合适的嵌入模型**: 选择适合任务的嵌入模型
3. **定期清理**: 定期清理不需要的数据
4. **监控资源**: 监控内存和磁盘使用情况

## 下一步

1. 查看 [ARCHITECTURE_EVOLUTION.md](../ARCHITECTURE_EVOLUTION.md) 了解架构详情
2. 运行测试验证功能: `python tests/test_new_architecture_simple.py`
3. 查看示例代码: `examples/vector_db_usage.py`
4. 参与贡献: 查看 CONTRIBUTING.md