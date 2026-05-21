# RAG 知识库问答系统

基于本地大模型的离线 RAG（检索增强生成）知识库问答系统。

## 📋 更新日志

### 🎯 最新更新 (2026-05-21)

✅ **问题修复**：解决了 "未找到相关文档" 错误
- 🔧 **修复了文档加载问题**：安装缺失的依赖包 `pypdf` 和 `docx2txt`
- 🔧 **修复了 ChromaDB API 兼容性**：适配最新 langchain-chroma 版本
- 🔧 **更新了嵌入模型**：改用本地 Ollama 模型 `mofanke/dmeta-embedding-zh`

✅ **系统状态**：向量数据库已重建，包含 428 个向量，支持所有文档格式

### 📅 历史更新

#### 2026-05-21
- ✅ **Docker 部署**：添加 Dockerfile 和 docker-compose.yml
- ✅ **部署脚本**：添加一键部署脚本（Linux/Mac/Windows）
- ✅ **部署文档**：添加详细部署指南

#### 2026-05-20
- ✅ **项目标准化**：标准化项目结构
- ✅ **配置解耦**：提取所有硬编码到配置文件
- ✅ **异常处理**：完善异常捕获和日志系统
- ✅ **打包部署**：添加可执行文件打包功能

#### 2026-05-19
- ✅ **Web 界面**：基于 Gradio 的 Web 应用
- ✅ **文档管理**：文档列表显示和刷新功能
- ✅ **RAG 问答**：基于本地大模型的智能问答

### 🔄 系统状态
- **向量数据库**：✅ 正常 (428 个向量)
- **文档处理**：✅ 正常 (支持 PDF/TXT/DOCX)
- **大模型**：✅ 正常 (Ollama Qwen 4B)
- **Web 应用**：✅ 正常 (Gradio 6.x)
- **部署支持**：✅ 正常 (Docker + 本地)

## 功能特性

- 📚 **文档管理**：支持 PDF、TXT、DOCX 格式文档上传和管理
- 🔍 **智能检索**：基于向量数据库的语义检索
- 🤖 **本地大模型**：使用 Ollama 本地大模型，全程离线运行
- 🎯 **重排优化**：MMR（最大边际相关性）检索重排
- 🌐 **Web 界面**：基于 Gradio 6.x 的友好用户界面
- 📊 **实时监控**：完整的日志和异常处理
- 🐳 **容器化部署**：支持 Docker 一键部署
- 🔄 **自动刷新**：文档列表自动刷新和手动刷新功能

## 项目结构

```
my-rag-project/
├── config/              # 配置文件
│   ├── __init__.py
│   ├── settings.py      # 应用配置
│   └── logging_config.py # 日志配置
├── core/                # 核心功能模块
│   ├── __init__.py
│   ├── llm_utils.py     # 大模型工具
│   ├── loader_utils.py  # 文档加载器
│   ├── vector_utils.py  # 向量数据库工具
│   └── exceptions.py    # 自定义异常
├── docs/                # 知识库文档
│   ├── test.txt
│   ├── test.pdf
│   └── test.docx
├── logs/                # 日志文件目录
├── model_cache/         # 模型缓存目录
├── res/                 # 资源文件
│   └── chroma_db/       # 向量数据库
├── scripts/             # 脚本文件
│   └── build_exe.py     # 打包脚本
├── tests/               # 测试文件
├── utils/               # 工具函数
│   ├── __init__.py
│   └── file_utils.py    # 文件工具
├── web/                 # Web 应用
│   ├── __init__.py
│   └── app.py           # Web 应用主文件
├── main.py              # 命令行入口
├── web_rag_app.py       # Web 应用入口
├── requirements.txt     # 依赖包列表
├── .env.example         # 环境变量示例
├── .gitignore          # Git 忽略文件
├── Dockerfile          # Docker 构建文件
├── docker-compose.yml  # Docker 编排文件
├── deploy.sh           # 部署脚本（Linux/Mac）
├── deploy.bat          # 部署脚本（Windows）
├── test_docker.sh      # Docker 测试脚本（Linux/Mac）
├── test_docker.bat     # Docker 测试脚本（Windows）
├── DEPLOYMENT.md       # 详细部署文档
├── QUICK_DEPLOY.md     # 快速部署指南
└── README.md           # 项目说明
```

## 🐳 Docker 容器化部署（推荐）

### 一键部署

#### Linux/Mac
```bash
git clone <项目地址>
cd my-rag-project
./deploy.sh full
```

#### Windows
```cmd
git clone <项目地址>
cd my-rag-project
deploy.bat full
```

### 手动部署
```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 访问应用
# Web 应用: http://localhost:7801
# Ollama API: http://localhost:11434
```

### 服务管理
```bash
# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 清理资源
docker-compose down -v
```

详细部署文档请参考 [DEPLOYMENT.md](DEPLOYMENT.md) 或 [QUICK_DEPLOY.md](QUICK_DEPLOY.md)。

## 🚀 快速开始

### 方式一：Docker 一键部署（推荐）

#### Linux/Mac
```bash
git clone <项目地址>
cd my-rag-project
./deploy.sh full
```

#### Windows
```cmd
git clone <项目地址>
cd my-rag-project
deploy.bat full
```

### 方式二：本地开发部署

#### 1. 环境配置
```bash
# 克隆项目
git clone <项目地址>
cd my-rag-project

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Ollama（如果未安装）
# 访问 https://ollama.com/ 下载安装

# 拉取所需模型
ollama pull qwen:4b
ollama pull mofanke/dmeta-embedding-zh
```

#### 2. 配置环境变量
```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件（可选）
# 主要配置项：
# - APP_PORT: Web 应用端口（默认 7801）
# - OLLAMA_LLM_MODEL: 大模型名称（默认 qwen:4b）
# - OLLAMA_EMBEDDING_MODEL: 嵌入模型（默认 mofanke/dmeta-embedding-zh）
```

#### 3. 初始化知识库
```bash
# 创建向量数据库（处理 docs/ 目录下的所有文档）
python main.py create --force

# 验证向量数据库状态
python main.py info
```

#### 4. 启动应用
```bash
# 启动 Web 应用
python web_rag_app.py

# 访问 http://localhost:7801
```

### 方式三：命令行工具使用

#### 查看帮助
```bash
python main.py --help
```

#### 创建向量数据库
```bash
# 创建新的向量数据库
python main.py create

# 强制重建（删除现有数据库）
python main.py create --force
```

#### 搜索文档
```bash
# 搜索相关文档
python main.py search "AI应用的技术架构如何设计"
```

#### RAG 问答
```bash
# 基于知识库的问答
python main.py chat "AI应用的技术架构如何设计"
```

#### 系统信息
```bash
# 查看系统状态
python main.py info
```

### 📱 Web 应用使用说明

1. **文档管理**：
   - 左侧显示文档列表
   - 支持自动刷新和手动刷新
   - 显示文档大小和状态

2. **知识库构建**：
   - 点击"一键构建知识库"按钮
   - 系统自动处理所有文档
   - 显示处理进度和结果

3. **智能问答**：
   - 在右侧输入问题
   - 系统基于知识库生成回答
   - 显示检索到的相关文档

4. **系统监控**：
   - 实时显示系统状态
   - 查看处理日志
   - 监控向量数据库状态

## ⚙️ 配置说明

### 模型配置
- **大模型**：Ollama Qwen 4B（可配置其他模型）
- **嵌入模型**：Ollama `mofanke/dmeta-embedding-zh`（本地中文嵌入模型）
- **向量数据库**：ChromaDB（本地持久化）

### 路径配置
- **文档目录**：`./docs`（存放知识库文档）
- **向量数据库**：`./res/chroma_db`（向量数据存储）
- **模型缓存**：`./model_cache`（模型缓存目录）
- **日志目录**：`./logs`（应用日志文件）

### 环境变量配置
复制 `.env.example` 为 `.env` 并修改：

```bash
# 应用配置
APP_HOST=0.0.0.0
APP_PORT=7801

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=qwen:4b
OLLAMA_EMBEDDING_MODEL=mofanke/dmeta-embedding-zh

# 向量数据库配置
VECTOR_DB_DIR=./res/chroma_db
VECTOR_DB_COLLECTION=rag_knowledge_base

# 文档处理配置
DOCS_DIR=./docs
CHUNK_SIZE=800
CHUNK_OVERLAP=150

# 检索配置
DEFAULT_TOP_K=3
SEARCH_TYPE=mmr
FETCH_K=10
LAMBDA_MULT=0.5
```

## 🏗️ 技术架构

### 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    RAG 知识库问答系统                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  文档处理层  │  │  向量检索层  │  │   大模型推理层      │ │
│  │ - 文档加载   │  │ - 向量化     │  │ - 提示工程         │ │
│  │ - 文档清洗   │  │ - 相似度检索 │  │ - 上下文构建       │ │
│  │ - 文档分割   │  │ - MMR重排    │  │ - 回答生成         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │                   数据存储层                           │ │
│  │  - 向量数据库 (ChromaDB)                              │ │
│  │  - 本地文件系统 (文档存储)                            │ │
│  │  - 模型缓存 (Ollama)                                  │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │                   用户界面层                           │ │
│  │  - Web 界面 (Gradio)                                  │ │
│  │  - 命令行工具 (CLI)                                   │ │
│  │  - API 接口 (RESTful)                                 │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件说明

#### 1. **文档处理模块** (`core/loader_utils.py`)
- **功能**：加载、清洗、分割文档
- **支持格式**：PDF, TXT, DOCX
- **关键技术**：文本分块、编码处理、质量过滤

#### 2. **向量数据库模块** (`core/vector_utils.py`)
- **功能**：文档向量化、存储、检索
- **数据库**：ChromaDB（本地持久化）
- **嵌入模型**：Ollama `mofanke/dmeta-embedding-zh`
- **检索算法**：相似度检索 + MMR 重排

#### 3. **大模型模块** (`core/llm_utils.py`)
- **功能**：RAG 问答链构建、提示工程、回答生成
- **模型**：Ollama Qwen 4B（可配置）
- **关键技术**：上下文压缩、流式输出、温度控制

#### 4. **Web 应用模块** (`web/app.py`)
- **框架**：Gradio 6.x
- **功能**：文档管理、知识库构建、智能问答
- **特性**：实时刷新、状态监控、错误处理

#### 5. **配置管理模块** (`config/settings.py`)
- **功能**：集中式配置管理
- **技术**：Pydantic BaseSettings
- **特性**：环境变量支持、类型验证、默认值

### 工作流程
1. **文档处理流程**：
   ```
   原始文档 → 加载 → 清洗 → 分割 → 向量化 → 存储到 ChromaDB
   ```

2. **问答流程**：
   ```
   用户问题 → 向量检索 → 文档重排 → 上下文构建 → 大模型生成 → 返回答案
   ```

3. **系统启动流程**：
   ```
   检查配置 → 加载向量数据库 → 启动大模型 → 启动 Web 服务
   ```

## 🛠️ 开发指南

### 添加新功能
1. **创建模块**：在 `core/` 目录下创建新模块
2. **添加配置**：在 `config/settings.py` 中添加相关配置
3. **更新依赖**：在 `requirements.txt` 中添加所需包
4. **编写测试**：在 `tests/` 目录下编写测试用例
5. **更新文档**：更新 README 和相关文档

### 代码规范
- **命名规范**：使用 snake_case 命名函数和变量
- **类型提示**：所有函数都应有类型提示
- **错误处理**：使用自定义异常类进行错误处理
- **日志记录**：使用统一的日志记录器

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看向量数据库操作日志
grep "vector" logs/app.log

# 查看文档处理日志
grep "loader" logs/app.log
```

### 性能优化建议
1. **文档处理**：
   - 使用缓存避免重复处理
   - 批量处理大文档
   - 并行处理多个文档

2. **向量检索**：
   - 调整 chunk_size 和 chunk_overlap
   - 优化 MMR 参数（lambda_mult, fetch_k）
   - 使用索引加速检索

3. **大模型推理**：
   - 调整 temperature 控制生成多样性
   - 使用流式输出减少等待时间
   - 缓存常见问题的回答

## 部署

### 打包为可执行文件
```bash
python scripts/build_exe.py
```

### Docker 部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 7801
CMD ["python", "web_rag_app.py"]
```

## 🔧 故障排除与常见问题

### 🚨 常见问题解决方案

#### 1. **"未找到相关文档" 错误**
**症状**：检索时提示 "未找到相关文档" 或 "No relevant documents found"
**原因**：
- 向量数据库为空或未正确创建
- 文档加载失败（缺少依赖）
- 嵌入模型配置错误

**解决方案**：
```bash
# 1. 检查并安装缺失依赖
pip install pypdf docx2txt

# 2. 强制重建向量数据库
python main.py create --force

# 3. 验证向量数据库状态
python main.py info
```

#### 2. **文档加载失败**
**症状**：PDF 或 DOCX 文件无法加载
**原因**：缺少 `pypdf` 或 `docx2txt` 包
**解决方案**：
```bash
pip install pypdf docx2txt
```

#### 3. **ChromaDB 创建失败**
**症状**：`'Chroma' object has no attribute 'persist'`
**原因**：langchain-chroma 版本兼容性问题
**解决方案**：已修复，无需额外操作

#### 4. **Ollama 模型未找到**
**症状**：`model "mofanke/dmeta-embedding-zh" not found`
**解决方案**：
```bash
# 拉取嵌入模型
ollama pull mofanke/dmeta-embedding-zh

# 拉取大模型
ollama pull qwen:4b
```

#### 5. **端口被占用**
**症状**：Web 应用无法启动
**解决方案**：
```bash
# 修改 .env 文件中的端口号
APP_PORT=7802  # 改为其他端口
```

#### 6. **Gradio 兼容性问题**
**症状**：`Chatbot.__init__() got an unexpected keyword argument 'type'`
**原因**：Gradio 6.x 版本 API 变更
**解决方案**：已修复，无需额外操作

### 📊 系统诊断命令

```bash
# 检查向量数据库状态
python main.py info

# 测试检索功能
python main.py search "测试查询"

# 测试 RAG 问答
python main.py chat "测试问题"

# 查看系统日志
tail -f logs/app.log
```

### 🔍 日志级别说明
- **DEBUG**: 详细调试信息（开发阶段使用）
- **INFO**: 常规运行信息（默认级别）
- **WARNING**: 警告信息（需要关注但非错误）
- **ERROR**: 错误信息（需要立即处理）
- **CRITICAL**: 严重错误（系统无法运行）

### 📋 快速检查清单
1. ✅ Ollama 服务是否运行：`ollama list`
2. ✅ 依赖包是否完整：`pip list | grep -E "pypdf|docx2txt|langchain"`
3. ✅ 向量数据库是否存在：检查 `res/chroma_db/` 目录
4. ✅ 环境变量是否正确：检查 `.env` 文件
5. ✅ 端口是否可用：检查端口 7801 是否被占用

## 许可证

MIT License

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 联系方式

如有问题或建议，请提交 Issue 或联系维护者。