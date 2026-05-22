# 向量数据库架构演进说明

## 概述

本文档描述了 RAG 知识库问答系统中向量数据库架构从 V1 到 V2 的演进过程。

## V1 架构（旧版）

### 架构特点
- **文件位置**: `core/vector_utils.py` 和 `core/vector_factory.py`
- **设计模式**: 简单的工厂模式
- **耦合度**: 较高，所有数据库逻辑集中在工厂类中
- **扩展性**: 较差，添加新数据库需要修改工厂类

### 主要组件
1. **VectorStoreFactory**: 工厂类，负责创建和加载所有类型的向量数据库
2. **统一接口**: 所有数据库通过相同的函数接口访问
3. **配置驱动**: 通过环境变量 `VECTOR_DB_TYPE` 切换数据库

### 优点
- 简单易用
- 统一接口
- 配置灵活

### 缺点
- 代码耦合度高
- 难以扩展新数据库类型
- 错误处理不够精细
- 缺乏类型安全

## V2 架构（新版）

### 架构特点
- **文件位置**: `core/vector_db/` 目录
- **设计模式**: 抽象基类 + 工厂模式 + 策略模式
- **耦合度**: 低，每个数据库独立实现
- **扩展性**: 优秀，添加新数据库只需创建新类

### 主要组件

#### 1. 抽象基类 (`base_vector_db.py`)
```python
class BaseVectorStore(ABC):
    def __init__(self, embedding: Embeddings):
        self.embedding = embedding
    
    @abstractmethod
    def add_documents(self, docs: List[Document]) -> None:
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        pass
    
    @abstractmethod
    def clear(self) -> None:
        pass
```

#### 2. 具体实现类
- `chroma_db.py`: ChromaDB 实现
- `faiss_db.py`: FAISS 实现
- `milvus_db.py`: Milvus 实现
- `qdrant_db.py`: Qdrant 实现

#### 3. 工厂类 (`vector_db_factory.py`)
```python
def get_vector_store(engine: str = "faiss", embedding: Optional[Embeddings] = None) -> BaseVectorStore:
    engine = engine.lower().strip()
    
    if engine == "chroma":
        from core.vector_db.chroma_db import ChromaStore
        return ChromaStore(embedding=embedding)
    # ... 其他数据库
```

#### 4. 高级接口 (`vector_utils.py`)
- 保持向后兼容
- 提供高级功能（如 MMR 重排）
- 错误处理和日志记录

### 架构优势

#### 1. **模块化设计**
```python
# 每个数据库独立实现
class ChromaStore(BaseVectorStore):
    def __init__(self, embedding, persist_dir="./resource/vector_db/chroma_db"):
        super().__init__(embedding)
        self.persist_dir = persist_dir
        self.db = Chroma(
            collection_name="knowledge_base",
            embedding_function=embedding,
            persist_directory=persist_dir
        )
```

#### 2. **类型安全**
- 完整的 Python 类型提示
- 抽象基类确保接口一致性
- 编译时类型检查

#### 3. **易于扩展**
```python
# 添加新数据库只需：
# 1. 创建新类继承 BaseVectorStore
# 2. 实现抽象方法
# 3. 在工厂类中添加映射
class NewVectorStore(BaseVectorStore):
    def __init__(self, embedding):
        super().__init__(embedding)
        # 初始化逻辑
    
    def add_documents(self, docs: List[Document]) -> None:
        # 实现添加文档逻辑
        pass
    
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        # 实现检索逻辑
        pass
    
    def clear(self) -> None:
        # 实现清空逻辑
        pass
```

#### 4. **错误隔离**
- 每个数据库的错误处理独立
- 不会因为一个数据库的错误影响其他功能
- 详细的错误日志和异常信息

#### 5. **配置灵活**
```python
# 通过环境变量配置
VECTOR_DB_TYPE=chroma  # chroma/faiss/milvus/qdrant

# 通过代码配置
store = get_vector_store(engine="faiss", embedding=embedding)
```

## 迁移指南

### 从 V1 迁移到 V2

#### 1. 导入路径变化
```python
# V1 (旧版)
from core.vector_factory import VectorStoreFactory

# V2 (新版)
from core.vector_db.vector_db_factory import get_vector_store
```

#### 2. 创建向量数据库
```python
# V1 (旧版)
vector_store = VectorStoreFactory.create_vector_store(
    documents=documents,
    embedding=embedding
)

# V2 (新版)
# 方法1: 使用高级接口（保持兼容）
from core.vector_utils import create_vector_store
vector_store = create_vector_store(documents, embedding)

# 方法2: 使用新架构
from core.vector_db.vector_db_factory import get_vector_store
store = get_vector_store(engine="chroma", embedding=embedding)
store.add_documents(documents)
```

#### 3. 加载向量数据库
```python
# V1 (旧版)
vector_store = VectorStoreFactory.load_vector_store(embedding)

# V2 (新版)
# 方法1: 使用高级接口
from core.vector_utils import load_existing_vector_store
vector_store = load_existing_vector_store()

# 方法2: 使用新架构
store = get_vector_store(engine="chroma", embedding=embedding)
# 注意：新架构需要显式加载文档
```

#### 4. 检索文档
```python
# V1 (旧版)
results = vector_store.similarity_search(query, k=top_k)

# V2 (新版)
# 方法1: 使用高级接口
from core.vector_utils import search_knowledge
context, docs = search_knowledge(query, top_k)

# 方法2: 使用新架构
results = store.search(query, top_k=top_k)
```

## 性能对比

### V1 架构性能
- **启动时间**: 中等
- **内存使用**: 较高（所有数据库逻辑在内存中）
- **扩展成本**: 高（需要修改核心工厂类）

### V2 架构性能
- **启动时间**: 快（按需加载）
- **内存使用**: 低（只加载需要的数据库）
- **扩展成本**: 低（只需添加新类）

## 最佳实践

### 1. 选择数据库类型
```python
# 开发环境：使用 ChromaDB
VECTOR_DB_TYPE=chroma

# 生产环境小规模：使用 FAISS
VECTOR_DB_TYPE=faiss

# 生产环境大规模：使用 Milvus 或 Qdrant
VECTOR_DB_TYPE=milvus
# 或
VECTOR_DB_TYPE=qdrant
```

### 2. 错误处理
```python
try:
    store = get_vector_store(engine="chroma", embedding=embedding)
    results = store.search(query, top_k=3)
except ValueError as e:
    print(f"配置错误: {e}")
except ConnectionError as e:
    print(f"连接错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

### 3. 性能优化
```python
# 批量添加文档
store.add_documents(documents)  # 一次添加多个文档

# 合理设置 top_k
results = store.search(query, top_k=5)  # 根据需求调整

# 定期清理
store.clear()  # 定期清理不需要的数据
```

## 未来规划

### 短期计划
1. **连接池**: 为远程数据库添加连接池支持
2. **缓存机制**: 添加查询结果缓存
3. **监控指标**: 添加性能监控和指标收集

### 长期计划
1. **分布式支持**: 支持分布式向量数据库
2. **自动切换**: 根据负载自动切换数据库类型
3. **AI优化**: 使用AI优化检索参数

## 总结

V2 架构在保持 V1 架构所有优点的同时，解决了其核心问题：

1. **解耦**: 每个数据库独立实现，互不影响
2. **可扩展**: 添加新数据库只需创建新类
3. **类型安全**: 完整的类型提示和检查
4. **错误隔离**: 错误不会在数据库间传播
5. **性能优化**: 按需加载，减少内存使用

新的架构为系统的长期发展和维护奠定了坚实的基础。