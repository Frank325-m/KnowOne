#!/usr/bin/env python3
"""
测试多向量数据库支持
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from core.vector_factory import VectorStoreFactory
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document


def test_vector_db_factory():
    """测试向量数据库工厂"""
    print("=" * 60)
    print("测试多向量数据库支持")
    print("=" * 60)
    
    # 测试文档
    test_documents = [
        Document(
            page_content="这是一个测试文档，用于验证向量数据库功能。",
            metadata={"source": "test", "page": 1}
        ),
        Document(
            page_content="人工智能是当前科技发展的重要方向。",
            metadata={"source": "test", "page": 2}
        ),
        Document(
            page_content="向量数据库用于存储和检索高维向量数据。",
            metadata={"source": "test", "page": 3}
        )
    ]
    
    # 获取嵌入模型
    print(f"\n1. 加载嵌入模型: {settings.EMBED_MODEL_NAME}")
    embedding = OllamaEmbeddings(model=settings.EMBED_MODEL_NAME)
    
    # 测试不同数据库类型
    db_types = ["chroma", "faiss"]  # 先测试本地数据库
    
    for db_type in db_types:
        print(f"\n{'='*40}")
        print(f"测试 {db_type.upper()} 向量数据库")
        print(f"{'='*40}")
        
        # 设置数据库类型
        settings.VECTOR_DB_TYPE = db_type
        
        try:
            # 测试创建
            print(f"\na) 创建 {db_type} 向量数据库...")
            vector_store = VectorStoreFactory.create_vector_store(
                documents=test_documents,
                embedding=embedding,
                collection_name="test_collection"
            )
            print(f"   ✓ 创建成功")
            
            # 测试加载
            print(f"\nb) 加载 {db_type} 向量数据库...")
            loaded_store = VectorStoreFactory.load_vector_store(
                embedding=embedding,
                collection_name="test_collection"
            )
            print(f"   ✓ 加载成功")
            
            # 测试信息获取
            print(f"\nc) 获取 {db_type} 向量数据库信息...")
            info = VectorStoreFactory.get_vector_store_info()
            print(f"   数据库信息: {info}")
            
            # 测试检索
            print(f"\nd) 测试 {db_type} 向量检索...")
            results = loaded_store.similarity_search("人工智能", k=2)
            print(f"   检索结果数量: {len(results)}")
            for i, doc in enumerate(results):
                print(f"   结果 {i+1}: {doc.page_content[:50]}...")
            
            print(f"\n✓ {db_type.upper()} 测试通过")
            
        except Exception as e:
            print(f"\n✗ {db_type.upper()} 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("远程数据库测试 (需要相应服务运行)")
    print(f"{'='*60}")
    
    # 测试远程数据库（需要相应服务）
    remote_db_types = ["milvus", "qdrant"]
    
    for db_type in remote_db_types:
        print(f"\n{'='*40}")
        print(f"测试 {db_type.upper()} 向量数据库 (连接测试)")
        print(f"{'='*40}")
        
        settings.VECTOR_DB_TYPE = db_type
        
        try:
            # 测试信息获取（连接测试）
            print(f"\na) 测试 {db_type} 连接...")
            info = VectorStoreFactory.get_vector_store_info()
            print(f"   连接信息: {info}")
            
            if info.get("exists", False):
                print(f"   ✓ {db_type} 连接成功，集合存在")
            else:
                print(f"   ⚠ {db_type} 连接成功，但集合不存在")
                
        except Exception as e:
            print(f"\n✗ {db_type.upper()} 连接失败: {e}")
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_vector_db_factory()