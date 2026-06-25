# AGENTS.md - KnowOne 项目规则与关键信息

> **本文件是项目协作的关键依赖，所有参与者必须遵守。**
> **修改本文件必须经过团队评审通过，不得擅自变更。**

## 项目概述

- **项目**: KnowOne - RAG 知识库问答系统（Python 本地大模型）
- **入口**: `main.py`（命令行 + Web）

## 目录约定

```
KnowOne/
├── config/              # 配置
├── core/                # 核心模块
│   └── vector_db/       # 向量数据库实现
├── web/                 # Web 应用
├── tests/               # 测试（统一管理）
├── res/docs/            # 知识库源文档（用户上传）
├── resource/vector_db/  # 向量数据库存储（自动生成）
├── docs/                # 项目文档
├── main.py              # 统一入口
└── .env                 # 环境变量
```

- 测试文件放 `tests/`，用户文档放 `res/docs/`，向量数据库放 `resource/vector_db/`

## 技术栈

- **LLM**: Ollama（默认 qwen:4b）
- **嵌入**: Ollama Embeddings（默认 mofanke/dmeta-embedding-zh）
- **Web**: Gradio 6.x | **配置**: Pydantic 2.x + python-dotenv
- **向量数据库**: ChromaDB / FAISS（默认） / Milvus / Qdrant
- **核心依赖**: langchain-core, langchain-ollama

## 代码风格

- PEP 8，类名 `PascalCase`，函数/变量 `snake_case`，常量 `UPPER_SNAKE_CASE`
- 必须使用类型注解，函数注释 Google 风格（中文），错误信息中文
- 禁止硬编码配置值，统一 `.env` 管理
- 使用项目自定义异常（`core/exceptions.py`）

## 向量数据库

- 工厂模式创建，所有实现继承 `BaseVectorStore`，通过 `VECTOR_DB_TYPE` 切换，默认 `faiss`
- 新增流程：`core/vector_db/` 创建文件 → 实现接口 → 工厂注册

## 开发工作流

1. 分析需求 → 2. 搜索代码 → 3. 制定方案 → 4. 执行修改 → 5. 测试验证 → 6. 更新文档

- **沟通格式**: `[动作] [目标] [详情]`（新增/修改/修复/优化/文档）
- **需确认**: 架构变更、删除文件、影响核心功能
- **修改后必检**: `python main.py test` + `python -m py_compile <file>`

## 关键配置（.env）

```bash
VECTOR_DB_TYPE=faiss          # chroma/faiss/milvus/qdrant
LLM_MODEL_NAME=qwen:4b
EMBED_MODEL_NAME=mofanke/dmeta-embedding-zh
CHUNK_SIZE=800 | CHUNK_OVERLAP=150
```

## 协作治理

- AGENTS.md 是项目唯一规则源，禁止创建重复规则文件
- 修改需团队评审通过（至少 1 人 approve）
- AI 助手不得擅自修改本文件，需说明原因并等待确认
