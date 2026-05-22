#!/usr/bin/env python3
"""
向量数据库使用示例
展示新的向量数据库架构的实际应用
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


def demo_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("基本使用示例")
    print("=" * 60)
    
    # 1. 创建嵌入模型
    print("1. 创建嵌入模型...")
    embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
    
    # 2. 创建向量数据库实例
    print("2. 创建向量数据库实例...")
    vector_store = get_vector_store(engine="chroma", embedding=embedding)
    
    # 3. 准备文档
    print("3. 准备文档...")
    documents = [
        Document(
            page_content="Python 是一种高级编程语言，以简洁易读著称。",
            metadata={"language": "python", "type": "编程语言", "popularity": "高"}
        ),
        Document(
            page_content="Java 是一种面向对象的编程语言，广泛应用于企业级开发。",
            metadata={"language": "java", "type": "编程语言", "popularity": "高"}
        ),
        Document(
            page_content="JavaScript 是用于网页开发的脚本语言，支持前端和后端开发。",
            metadata={"language": "javascript", "type": "脚本语言", "popularity": "高"}
        ),
        Document(
            page_content="人工智能是计算机科学的一个分支，致力于创建智能机器。",
            metadata={"field": "AI", "type": "科技领域", "trend": "热门"}
        ),
        Document(
            page_content="机器学习是人工智能的核心技术，使计算机能够从数据中学习。",
            metadata={"field": "AI", "type": "技术", "trend": "热门"}
        )
    ]
    
    # 4. 添加文档
    print("4. 添加文档到向量数据库...")
    vector_store.add_documents(documents)
    print(f"   已添加 {len(documents)} 个文档")
    
    # 5. 检索示例
    print("\n5. 检索示例:")
    queries = ["编程语言", "人工智能", "机器学习", "网页开发"]
    
    for query in queries:
        print(f"\n查询: '{query}'")
        results = vector_store.search(query, top_k=2)
        
        for i, doc in enumerate(results):
            print(f"  结果 {i+1}: {doc.page_content[:50]}...")
            print(f"      元数据: {doc.metadata}")
    
    # 6. 清理（可选）
    print("\n6. 清理...")
    try:
        vector_store.clear()
        print("   数据库已清理")
    except Exception as e:
        print(f"   清理时出现警告: {e}")
    
    print("\n基本使用示例完成！")


def demo_multiple_databases():
    """多数据库示例"""
    print("\n" + "=" * 60)
    print("多数据库示例")
    print("=" * 60)
    
    # 创建嵌入模型
    embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
    
    # 测试不同数据库
    databases = [
        ("chroma", "ChromaDB (本地轻量级)"),
        ("faiss", "FAISS (高性能相似性搜索)"),
        # ("milvus", "Milvus (云原生向量数据库)"),  # 需要运行服务
        # ("qdrant", "Qdrant (高性能向量搜索引擎)")  # 需要运行服务
    ]
    
    test_documents = [
        Document(page_content="向量数据库用于存储和检索高维向量数据。", metadata={"topic": "向量数据库"}),
        Document(page_content="相似性搜索是向量数据库的核心功能。", metadata={"topic": "搜索算法"}),
        Document(page_content="嵌入模型将文本转换为向量表示。", metadata={"topic": "自然语言处理"})
    ]
    
    for db_type, db_name in databases:
        print(f"\n测试 {db_name}:")
        
        try:
            # 创建数据库实例
            vector_store = get_vector_store(engine=db_type, embedding=embedding)
            
            # 添加文档
            vector_store.add_documents(test_documents)
            print(f"  [OK] 文档添加成功")
            
            # 检索测试
            results = vector_store.search("向量数据库", top_k=1)
            if results:
                print(f"  [OK] 检索成功: {results[0].page_content[:40]}...")
            else:
                print(f"  [ERROR] 检索失败")
            
            # 清理
            try:
                vector_store.clear()
                print(f"  [OK] 清理成功")
            except:
                print(f"  [WARN] 清理时出现警告")
                
        except Exception as e:
            print(f"  ✗ {db_name} 测试失败: {e}")
            if "No module named" in str(e):
                print(f"    提示: 可能需要安装额外的依赖包")
    
    print("\n多数据库示例完成！")


def demo_custom_implementation():
    """自定义实现示例"""
    print("\n" + "=" * 60)
    print("自定义实现示例")
    print("=" * 60)
    
    from typing import List
    from core.vector_db.base_vector_db import BaseVectorStore
    
    # 创建自定义向量存储
    class SimpleMemoryStore(BaseVectorStore):
        """简单的内存向量存储（用于演示）"""
        
        def __init__(self, embedding):
            super().__init__(embedding)
            self.documents = []
            print("  创建 SimpleMemoryStore 实例")
        
        def add_documents(self, docs: List[Document]) -> None:
            self.documents.extend(docs)
            print(f"  添加了 {len(docs)} 个文档，总计 {len(self.documents)} 个文档")
        
        def search(self, query: str, top_k: int = 3) -> List[Document]:
            # 简单的关键词匹配（实际应用中应该使用向量相似性）
            results = []
            for doc in self.documents:
                if query.lower() in doc.page_content.lower():
                    results.append(doc)
                if len(results) >= top_k:
                    break
            print(f"  查询 '{query}' 返回 {len(results)} 个结果")
            return results
        
        def clear(self) -> None:
            self.documents.clear()
            print("  已清空所有文档")
    
    # 使用自定义存储
    embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
    custom_store = SimpleMemoryStore(embedding)
    
    # 添加文档
    docs = [
        Document(page_content="自定义向量存储示例文档1", metadata={"id": 1}),
        Document(page_content="自定义向量存储示例文档2", metadata={"id": 2}),
        Document(page_content="另一个测试文档", metadata={"id": 3})
    ]
    custom_store.add_documents(docs)
    
    # 检索
    results = custom_store.search("自定义", top_k=2)
    print(f"  检索结果数量: {len(results)}")
    
    # 清理
    custom_store.clear()
    
    print("\n自定义实现示例完成！")


def demo_integration_with_rag():
    """与RAG系统集成示例"""
    print("\n" + "=" * 60)
    print("与RAG系统集成示例")
    print("=" * 60)
    
    # 模拟RAG流程
    print("模拟RAG问答流程:")
    print("1. 用户提问 -> 2. 检索相关文档 -> 3. 生成回答")
    
    # 创建知识库
    embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
    knowledge_base = get_vector_store(engine="chroma", embedding=embedding)
    
    # 添加知识文档
    knowledge_docs = [
        Document(
            page_content="Ollama 是一个本地大模型运行框架，支持多种开源模型。",
            metadata={"source": "ollama_docs", "topic": "大模型框架"}
        ),
        Document(
            page_content="LangChain 是一个用于构建大模型应用的框架，提供链式调用和工具集成。",
            metadata={"source": "langchain_docs", "topic": "AI框架"}
        ),
        Document(
            page_content="RAG（检索增强生成）结合了检索系统和生成模型，提高回答的准确性和相关性。",
            metadata={"source": "rag_paper", "topic": "AI技术"}
        ),
        Document(
            page_content="向量数据库是RAG系统的核心组件，用于存储和检索文档向量。",
            metadata={"source": "vector_db_guide", "topic": "存储技术"}
        )
    ]
    
    knowledge_base.add_documents(knowledge_docs)
    print(f"  知识库已构建，包含 {len(knowledge_docs)} 个文档")
    
    # 模拟用户问题
    user_questions = [
        "什么是 Ollama？",
        "RAG 系统如何工作？",
        "向量数据库在AI中有什么作用？"
    ]
    
    for question in user_questions:
        print(f"\n用户问题: {question}")
        
        # 检索相关文档
        relevant_docs = knowledge_base.search(question, top_k=2)
        
        if relevant_docs:
            print(f"  检索到 {len(relevant_docs)} 个相关文档:")
            for i, doc in enumerate(relevant_docs):
                print(f"    文档{i+1}: {doc.page_content[:60]}...")
            
            # 模拟生成回答（简化版）
            context = " ".join([doc.page_content for doc in relevant_docs[:2]])
            print(f"  生成回答（基于检索内容）...")
            # 实际应用中这里会调用大模型生成回答
        else:
            print(f"  未找到相关文档")
    
    # 清理
    try:
        knowledge_base.clear()
        print("\n  知识库已清理")
    except:
        print("\n  清理知识库时出现警告")
    
    print("\nRAG集成示例完成！")


def main():
    """主函数"""
    print("向量数据库架构演示")
    print("=" * 60)
    
    # 运行所有演示
    demos = [
        ("基本使用", demo_basic_usage),
        ("多数据库", demo_multiple_databases),
        ("自定义实现", demo_custom_implementation),
        ("RAG集成", demo_integration_with_rag)
    ]
    
    for demo_name, demo_func in demos:
        print(f"\n[运行演示] {demo_name}")
        try:
            demo_func()
            print(f"  [完成] {demo_name} 演示")
        except Exception as e:
            print(f"  [错误] {demo_name} 演示失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("所有演示完成！")
    print("=" * 60)
    print("\n总结:")
    print("1. 新的向量数据库架构提供了统一的接口")
    print("2. 支持多种向量数据库（ChromaDB、FAISS、Milvus、Qdrant）")
    print("3. 易于扩展和自定义实现")
    print("4. 与RAG系统完美集成")
    print("\n查看完整文档:")
    print("- README.md: 项目概述和架构说明")
    print("- docs/guides/VECTOR_DB_QUICK_START.md: 快速使用指南")
    print("- docs/guides/ARCHITECTURE_EVOLUTION.md: 架构演进详情")


if __name__ == "__main__":
    main()