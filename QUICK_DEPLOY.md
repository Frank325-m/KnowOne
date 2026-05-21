# RAG 知识库问答系统 - 快速部署指南

## 🚀 一键部署

### Linux/Mac
```bash
# 1. 克隆项目
git clone <项目地址>
cd my-rag-project

# 2. 一键部署
./deploy.sh full
```

### Windows
```cmd
# 1. 克隆项目
git clone <项目地址>
cd my-rag-project

# 2. 一键部署
deploy.bat full
```

## 📁 项目结构

```
my-rag-project/
├── docs/                    # 文档目录（放入您的文档）
├── res/                    # 向量数据库
├── logs/                   # 日志文件
├── config/                 # 配置文件
├── core/                   # 核心功能模块
├── utils/                  # 工具函数
├── web/                    # Web应用模块
├── Dockerfile             # Docker构建文件
├── docker-compose.yml     # Docker编排文件
├── deploy.sh              # 部署脚本（Linux/Mac）
├── deploy.bat             # 部署脚本（Windows）
├── requirements.txt       # Python依赖
└── web_rag_app.py         # Web应用入口
```

## 🔧 基本配置

### 1. 准备文档
将您的文档（txt, pdf, docx格式）放入 `docs/` 目录：
```bash
# 创建文档目录
mkdir -p docs

# 复制您的文档到 docs/ 目录
cp your_documents/* docs/
```

### 2. 环境配置（可选）
如果需要自定义配置：
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

主要配置项：
```env
# 模型配置
LLM_MODEL_NAME="qwen:4b"                    # 问答模型
EMBED_MODEL_NAME="mofanke/dmeta-embedding-zh" # 嵌入模型

# 服务端口
WEB_PORT=7801                               # Web应用端口

# 文档处理
CHUNK_SIZE=800                              # 文本块大小
CHUNK_OVERLAP=150                           # 块重叠大小
```

## 🐳 Docker 部署

### 手动部署步骤
```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

### 服务管理
```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 清理所有资源
docker-compose down -v
docker system prune -f
```

## 🌐 访问应用

部署完成后，通过以下地址访问：

- **Web 应用**: http://localhost:7801
- **Ollama API**: http://localhost:11434

## 📊 系统功能

### 1. 文档管理
- 自动扫描 `docs/` 目录中的文档
- 支持 txt, pdf, docx 格式
- 实时刷新文档列表

### 2. 智能问答
- 基于文档内容的问答
- 支持上下文理解
- 提供相关文档引用

### 3. 系统管理
- 系统状态监控
- 向量数据库管理
- 模型连接测试

## 🔍 常见问题

### Q1: 端口被占用怎么办？
修改 `.env` 文件中的 `WEB_PORT` 配置，然后重启服务。

### Q2: 如何添加新文档？
将新文档放入 `docs/` 目录，然后在 Web 界面点击"刷新文档列表"。

### Q3: 如何更换模型？
修改 `.env` 文件中的模型配置，然后重启服务。

### Q4: 如何查看日志？
```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f rag-app
```

## 🛠️ 高级功能

### 初始化向量数据库
```bash
# 手动初始化
./deploy.sh init

# 或使用 Docker
docker-compose run --rm vector-db-init
```

### 备份数据
```bash
# 备份向量数据库
tar -czf backup_$(date +%Y%m%d).tar.gz res/

# 备份文档
tar -czf docs_backup_$(date +%Y%m%d).tar.gz docs/
```

### 恢复数据
```bash
# 停止服务
docker-compose down

# 恢复备份
tar -xzf backup_20240101.tar.gz
tar -xzf docs_backup_20240101.tar.gz

# 启动服务
docker-compose up -d
```

## 📈 性能优化

### 硬件建议
- **CPU**: 4核以上
- **内存**: 8GB以上
- **存储**: SSD推荐

### 配置优化
- 调整 `CHUNK_SIZE` 优化文档处理
- 调整 `DEFAULT_TOP_K` 优化检索性能
- 启用缓存提高响应速度

## 🔒 安全建议

### 生产环境部署
1. 使用 HTTPS 加密通信
2. 配置防火墙规则
3. 定期备份数据
4. 监控系统日志

### 访问控制
1. 实现用户认证
2. 限制访问频率
3. 记录操作日志

## 📞 技术支持

遇到问题请：
1. 查看本文档的常见问题部分
2. 检查系统日志定位问题
3. 查看详细部署文档 `DEPLOYMENT.md`
4. 联系技术支持

---

**部署完成！** 🎉

现在您可以访问 http://localhost:7801 开始使用 RAG 知识库问答系统了！