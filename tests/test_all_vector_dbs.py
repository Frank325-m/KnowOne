"""
测试所有4个向量数据库
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from core.vector_db.vector_db_factory import get_vector_store

def test_vector_db(db_type: str, db_name: str):
    """测试指定的向量数据库"""
    print(f"\n{'='*60}")
    print(f"测试 {db_name} ({db_type})")
    print(f"{'='*60}")
    
    try:
        # 创建嵌入模型
        embedding = OllamaEmbeddings(model="mofanke/dmeta-embedding-zh")
        
        # 创建向量数据库
        print(f"1. 创建向量数据库...")
        vector_store = get_vector_store(engine=db_type, embedding=embedding)
        print(f"   [OK] {db_name} 创建成功")
        print(f"   持久化目录: {vector_store.persist_dir}")
        
        # 测试文档
        test_docs = [
            Document(
                page_content="人工智能是当前科技发展的重要方向，它正在改变我们的生活方式。",
                metadata={"source": "test1", "topic": "AI"}
            ),
            Document(
                page_content="机器学习是人工智能的核心技术之一，它通过数据学习来改进性能。",
                metadata={"source": "test2", "topic": "ML"}
            ),
            Document(
                page_content="深度学习是机器学习的一个分支，它使用神经网络来学习复杂的模式。",
                metadata={"source": "test3", "topic": "Deep Learning"}
            ),
            Document(
                page_content="RAG技术结合了检索和生成，能够提供更加准确和可追溯的回答。",
                metadata={"source": "test4", "topic": "RAG"}
            ),
        ]
        
        # 测试添加文档
        print(f"\n2. 添加文档...")
        vector_store.add_documents(test_docs)
        print(f"   [OK] 添加了 {len(test_docs)} 个文档")
        
        # 测试获取文档数量
        print(f"\n3. 测试获取文档数量...")
        count = vector_store.get_document_count()
        print(f"   [OK] 文档数量: {count}")
        if count != len(test_docs):
            print(f"   [WARNING] 文档数量不一致，期望: {len(test_docs)}, 实际: {count}")
        
        # 测试搜索
        print(f"\n4. 搜索测试...")
        query = "什么是人工智能？"
        results = vector_store.search(query, top_k=2)
        print(f"   查询: {query}")
        print(f"   找到 {len(results)} 个结果:")
        for i, doc in enumerate(results, 1):
            print(f"     {i}. {doc.page_content[:50]}...")
        
        # 测试清空
        print(f"\n5. 清空数据库...")
        vector_store.clear()
        print(f"   [OK] 数据库已清空")
        
        print(f"\n[OK] {db_name} 测试通过!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {db_name} 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("向量数据库测试套件")
    print("="*60)
    
    # 测试的数据库列表
    dbs_to_test = [
        ("faiss", "FAISS"),
        ("chroma", "ChromaDB"),
        # ("milvus", "Milvus"),  # 需要Milvus服务
        # ("qdrant", "Qdrant"),  # 需要Qdrant服务
    ]
    
    results = []
    for db_type, db_name in dbs_to_test:
        results.append((db_name, test_vector_db(db_type, db_name)))
    
    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    for db_name, result in results:
        status = "[OK] 通过" if result else "[ERROR] 失败"
        print(f"{db_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {len(results)} 个测试")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
