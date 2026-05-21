# RAG 知识库问答系统容器化部署指南

## 概述

本文档提供 RAG 知识库问答系统的 Docker 容器化部署指南。系统包含以下组件：

1. **RAG Web 应用** - 基于 Gradio 的 Web 界面
2. **Ollama 服务** - 本地大模型服务
3. **向量数据库** - ChromaDB 向量存储

## 系统要求

### 硬件要求
- CPU: 4 核以上（推荐 8 核）
- 内存: 8GB 以上（推荐 16GB）
- 存储: 20GB 以上可用空间

### 软件要求
- Docker: 20.10+
- Docker Compose: 2.0+
- Git: 最新版本

## 快速开始

### 1. 克隆项目
```bash
git clone <项目地址>
cd my-rag-project
```

### 2. 准备文档
将您的文档放入 `docs/` 目录：
```bash
mkdir -p docs
# 将您的文档（txt, pdf, docx）复制到 docs/ 目录
```

### 3. 配置环境变量
```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，根据需要修改配置
# 主要配置项：
# - OLLAMA_MODEL: Ollama 模型名称（默认: qwen:4b）
# - EMBED_MODEL_NAME: 嵌入模型名称（默认: mofanke/dmeta-embedding-zh）
# - WEB_PORT: Web 服务端口（默认: 7801）
```

### 4. 完整部署（推荐）
```bash
# Linux/Mac
./deploy.sh full

# Windows
deploy.bat full
```

### 5. 访问应用
- RAG Web 应用: http://localhost:7801
- Ollama API: http://localhost:11434

## 手动部署步骤

### 1. 检查环境
```bash
# 检查 Docker 和 Docker Compose
docker --version
docker-compose --version
```

### 2. 构建镜像
```bash
docker-compose build
```

### 3. 启动服务
```bash
docker-compose up -d
```

### 4. 查看服务状态
```bash
docker-compose ps
```

### 5. 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f rag-app
docker-compose logs -f ollama
```

## 部署脚本使用

### Linux/Mac
```bash
# 查看帮助
./deploy.sh help

# 完整部署
./deploy.sh full

# 单独命令
./deploy.sh build      # 构建镜像
./deploy.sh start      # 启动服务
./deploy.sh stop       # 停止服务
./deploy.sh restart    # 重启服务
./deploy.sh logs       # 查看日志
./deploy.sh init       # 初始化向量数据库
./deploy.sh clean      # 清理资源
./deploy.sh status     # 查看状态
```

### Windows
```batch
# 查看帮助
deploy.bat help

# 完整部署
deploy.bat full

# 单独命令
deploy.bat build      # 构建镜像
deploy.bat start      # 启动服务
deploy.bat stop       # 停止服务
deploy.bat restart    # 重启服务
deploy.bat logs       # 查看日志
deploy.bat init       # 初始化向量数据库
deploy.bat clean      # 清理资源
deploy.bat status     # 查看状态
```

## 服务说明

### 1. RAG Web 应用 (`rag-app`)
- 端口: 7801
- 功能: 提供 Web 界面进行文档管理和问答
- 数据卷:
  - `./docs` -> `/app/docs` (文档目录)
  - `./res` -> `/app/res` (向量数据库)
  - `./logs` -> `/app/logs` (日志文件)
  - `./model_cache` -> `/app/model_cache` (模型缓存)

### 2. Ollama 服务 (`ollama`)
- 端口: 11434
- 功能: 提供本地大模型服务
- 数据卷: `ollama_data` (模型数据)
- 预装模型:
  - `qwen:4b` (问答模型)
  - `mofanke/dmeta-embedding-zh` (嵌入模型)

### 3. 向量数据库初始化服务 (`vector-db-init`)
- 一次性服务，用于初始化向量数据库
- 自动从 `docs/` 目录加载文档并创建向量索引

## 配置说明

### 环境变量配置 (`.env`)

```env
# Ollama 配置
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=qwen:4b

# 嵌入模型配置
EMBED_MODEL_NAME=mofanke/dmeta-embedding-zh

# Web 应用配置
WEB_HOST=0.0.0.0
WEB_PORT=7801
WEB_DEBUG=false
WEB_SHARE=false

# 文档处理配置
CHUNK_SIZE=800
CHUNK_OVERLAP=150
DEFAULT_TOP_K=3

# 日志配置
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

### Docker Compose 配置

主要配置项：
- **网络**: 使用 `rag-network` 桥接网络，服务间可互相访问
- **健康检查**: 所有服务都有健康检查机制
- **数据持久化**: 所有数据都通过卷持久化
- **资源限制**: 可根据需要添加资源限制

## 管理操作

### 更新模型
```bash
# 进入 Ollama 容器
docker exec -it rag-ollama bash

# 拉取新模型
ollama pull llama2:7b

# 或者在主机上执行
docker exec rag-ollama ollama pull llama2:7b
```

### 备份数据
```bash
# 备份向量数据库
tar -czf vector_db_backup.tar.gz res/

# 备份文档
tar -czf docs_backup.tar.gz docs/

# 备份日志
tar -czf logs_backup.tar.gz logs/
```

### 恢复数据
```bash
# 停止服务
docker-compose down

# 恢复数据
tar -xzf vector_db_backup.tar.gz
tar -xzf docs_backup.tar.gz
tar -xzf logs_backup.tar.gz

# 启动服务
docker-compose up -d
```

## 故障排除

### 1. 端口冲突
如果端口 7801 或 11434 被占用，修改 `.env` 文件中的端口配置：
```env
WEB_PORT=7802
# 并在 docker-compose.yml 中更新端口映射
```

### 2. 内存不足
如果内存不足，可以：
1. 使用更小的模型
2. 增加 Docker 内存限制
3. 减少并发请求

### 3. 模型下载失败
如果模型下载失败，检查网络连接，或手动下载：
```bash
# 手动下载模型到 Ollama
docker exec rag-ollama ollama pull qwen:4b
```

### 4. 查看详细日志
```bash
# 查看应用日志
docker-compose logs rag-app

# 查看 Ollama 日志
docker-compose logs ollama

# 查看所有服务的详细日志
docker-compose logs --tail=100 -f
```

## 性能优化建议

### 1. 硬件优化
- 使用 SSD 存储提高 I/O 性能
- 增加内存容量以支持更大模型
- 使用 GPU 加速（如果支持）

### 2. 配置优化
- 调整 `CHUNK_SIZE` 和 `CHUNK_OVERLAP` 优化文档处理
- 调整 `DEFAULT_TOP_K` 优化检索性能
- 启用缓存提高响应速度

### 3. 模型优化
- 根据需求选择合适的模型大小
- 使用量化模型减少内存占用
- 定期更新模型版本

## 安全建议

### 1. 网络安全
- 在生产环境中使用 HTTPS
- 配置防火墙限制访问
- 使用反向代理（如 Nginx）

### 2. 数据安全
- 定期备份重要数据
- 加密敏感文档
- 限制文档访问权限

### 3. 访问控制
- 实现用户认证
- 记录操作日志
- 设置访问频率限制

## 扩展部署

### 1. 集群部署
对于高并发场景，可以考虑：
- 使用 Kubernetes 部署
- 部署多个 RAG 应用实例
- 使用负载均衡器

### 2. 高可用部署
- 配置数据库主从复制
- 使用共享存储
- 实现自动故障转移

### 3. 监控告警
- 集成 Prometheus 监控
- 配置 Grafana 仪表板
- 设置告警规则

## 支持与帮助

如果遇到问题：
1. 查看本文档的故障排除部分
2. 检查项目 GitHub Issues
3. 查看详细日志定位问题
4. 联系技术支持

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持 Docker 容器化部署
- 包含完整的部署脚本
- 提供详细部署文档