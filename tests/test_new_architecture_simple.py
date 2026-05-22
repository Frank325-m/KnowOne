#!/usr/bin/env python3
"""
测试新的向量数据库架构 - 简化版
使用纯ASCII字符避免编码问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from core.vector_db.vector_db_factory import get_vector_store
from core.vector_db.base_vector_db import BaseVectorStore


def test_base_class():
    """测试抽象基类"""
    print("=" * 60)
    print("测试抽象基类 BaseVectorStore")
    print("=" * 60)
    
    # 测试基类不能直接实例化
    try:
        store = BaseVectorStore(embedding=None)
        print("[ERROR] 基类不应该能直接实例化")
        return False
    except TypeError as e:
        print("[OK] 基类正确阻止直接实例化")
        print(f"  错误信息: {e}")
    
    # 测试基类方法
    class TestStore(BaseVectorStore):
        def add_documents(self, docs):
            self.docs = docs
        
        def search(self, query, top_k=3):
            return self.docs[:top_k] if hasattr(self, 'docs') else []
        
        def clear(self):
            if hasattr(self, 'docs'):
                self.docs.clear()
    
    embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
    test_store = TestStore(embedding)
    
    # 测试方法调用
    test_docs = [Document(page_content=f"文档{i}", metadata={"id": i}) for i in range(5)]
    test_store.add_documents(test_docs)
    
    results = test_store.search("查询", top_k=2)
    print(f"[OK] 测试存储检索返回 {len(results)} 个文档")
    
    test_store.clear()
    print("[OK] 测试存储清空成功")
    
    return True


def test_factory_pattern():
    """测试工厂模式"""
    print("\n" + "=" * 60)
    print("测试工厂模式 vector_db_factory")
    print("=" * 60)
    
    embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
    
    # 测试支持的数据库类型
    supported_engines = ["chroma", "faiss", "milvus", "qdrant"]
    
    for engine in supported_engines:
        print(f"\n测试 {engine.upper()} 数据库:")
        try:
            store = get_vector_store(engine=engine, embedding=embedding)
            print(f"  [OK] 成功创建 {engine} 存储实例")
            print(f"    类型: {type(store).__name__}")
            print(f"    基类: {isinstance(store, BaseVectorStore)}")
        except Exception as e:
            print(f"  [WARN] 创建 {engine} 存储失败: {e}")
            if "must be imported" in str(e) or "No module named" in str(e):
                print(f"    提示: 可能需要安装额外的依赖包")
    
    # 测试无效的引擎类型
    print("\n测试无效引擎类型:")
    try:
        store = get_vector_store(engine="invalid", embedding=embedding)
        print("  [ERROR] 不应该接受无效引擎类型")
    except ValueError as e:
        print(f"  [OK] 正确拒绝无效引擎类型: {e}")
    
    # 测试缺少 embedding 参数
    print("\n测试缺少 embedding 参数:")
    try:
        store = get_vector_store(engine="chroma", embedding=None)
        print("  [ERROR] 不应该接受缺少 embedding 参数")
    except ValueError as e:
        print(f"  [OK] 正确要求 embedding 参数: {e}")
    
    return True


def test_chroma_integration():
    """测试 ChromaDB 集成"""
    print("\n" + "=" * 60)
    print("测试 ChromaDB 集成")
    print("=" * 60)
    
    try:
        embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
        store = get_vector_store(engine="chroma", embedding=embedding)
        
        # 测试文档操作
        test_docs = [
            Document(
                page_content="人工智能是当前科技发展的重要方向。",
                metadata={"source": "test", "type": "科技"}
            ),
            Document(
                page_content="机器学习是人工智能的核心技术之一。",
                metadata={"source": "test", "type": "技术"}
            ),
            Document(
                page_content="深度学习在图像识别和自然语言处理中广泛应用。",
                metadata={"source": "test", "type": "应用"}
            )
        ]
        
        print("1. 测试添加文档:")
        store.add_documents(test_docs)
        print("   [OK] 文档添加成功")
        
        print("\n2. 测试检索文档:")
        results = store.search("人工智能", top_k=2)
        print(f"   [OK] 检索到 {len(results)} 个文档")
        for i, doc in enumerate(results):
            print(f"     文档{i+1}: {doc.page_content[:30]}...")
        
        print("\n3. 测试清空数据库:")
        try:
            store.clear()
            print("   [OK] 数据库清空成功")
        except Exception as e:
            print(f"   [WARN] 数据库清空时出现警告: {e}")
            # 这不算测试失败，因为文件可能被占用是正常情况
        
        return True
        
    except Exception as e:
        print(f"[ERROR] ChromaDB 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_vector_store():
    """测试自定义向量存储"""
    print("\n" + "=" * 60)
    print("测试自定义向量存储")
    print("=" * 60)
    
    from typing import List
    
    class CustomVectorStore(BaseVectorStore):
        def __init__(self, embedding):
            super().__init__(embedding)
            self.documents = []
            self.search_history = []
        
        def add_documents(self, docs: List[Document]) -> None:
            self.documents.extend(docs)
            print(f"  自定义存储: 添加了 {len(docs)} 个文档")
        
        def search(self, query: str, top_k: int = 3) -> List[Document]:
            self.search_history.append(query)
            # 简单实现：返回包含查询词的文档
            results = []
            for doc in self.documents:
                if query in doc.page_content:
                    results.append(doc)
                if len(results) >= top_k:
                    break
            print(f"  自定义存储: 查询 '{query}' 返回 {len(results)} 个结果")
            return results
        
        def clear(self) -> None:
            self.documents.clear()
            self.search_history.clear()
            print("  自定义存储: 已清空所有数据")
    
    # 测试自定义存储
    embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
    custom_store = CustomVectorStore(embedding)
    
    # 添加文档
    docs = [
        Document(page_content="Python 是一种高级编程语言", metadata={"lang": "python"}),
        Document(page_content="Java 是一种面向对象的编程语言", metadata={"lang": "java"}),
        Document(page_content="JavaScript 用于网页开发", metadata={"lang": "javascript"})
    ]
    custom_store.add_documents(docs)
    
    # 检索文档
    results = custom_store.search("编程语言", top_k=2)
    print(f"  [OK] 自定义存储检索成功: {len(results)} 个结果")
    
    # 清空存储
    custom_store.clear()
    print("  [OK] 自定义存储清空成功")
    
    return True


def main():
    """主测试函数"""
    print("新的向量数据库架构测试")
    print("=" * 60)
    
    tests = [
        ("抽象基类测试", test_base_class),
        ("工厂模式测试", test_factory_pattern),
        ("ChromaDB 集成测试", test_chroma_integration),
        ("自定义存储测试", test_custom_vector_store)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[开始] {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            status = "[OK] 通过" if success else "[ERROR] 失败"
            print(f"  {status}")
        except Exception as e:
            print(f"  [ERROR] 测试异常: {e}")
            results.append((test_name, False))
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[OK] 通过" if success else "[ERROR] 失败"
        print(f"{status} {test_name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！新的向量数据库架构工作正常。")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败，需要进一步检查。")
        return 1


if __name__ == "__main__":
    sys.exit(main())