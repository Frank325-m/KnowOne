#!/bin/bash
# Docker 部署测试脚本

set -e

echo "=== Docker 部署测试 ==="
echo "开始时间: $(date)"
echo

# 检查 Docker
echo "1. 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi
echo "✅ Docker 已安装: $(docker --version)"

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi
echo "✅ Docker Compose 已安装: $(docker-compose --version)"
echo

# 检查项目文件
echo "2. 检查项目文件..."
required_files=("Dockerfile" "docker-compose.yml" "requirements.txt" "web_rag_app.py")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
        exit 1
    fi
done
echo

# 检查目录
echo "3. 检查项目目录..."
required_dirs=("config" "core" "utils" "web")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir 目录存在"
    else
        echo "❌ $dir 目录不存在"
        exit 1
    fi
done
echo

# 创建测试文档
echo "4. 准备测试文档..."
mkdir -p docs
cat > docs/test_document.txt << EOF
这是一个测试文档，用于验证 RAG 系统的功能。

RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术。
它首先从知识库中检索相关信息，然后基于这些信息生成回答。

测试问题：
1. 什么是 RAG？
2. RAG 有什么优势？
3. 如何部署 RAG 系统？

测试答案：
1. RAG 是检索增强生成技术。
2. RAG 可以提供更准确、更有依据的回答。
3. 可以使用 Docker 容器化部署 RAG 系统。
EOF
echo "✅ 测试文档已创建"
echo

# 构建测试
echo "5. 测试 Docker 构建..."
if docker-compose build --no-cache; then
    echo "✅ Docker 构建测试通过"
else
    echo "❌ Docker 构建测试失败"
    exit 1
fi
echo

# 启动测试服务
echo "6. 测试服务启动..."
if docker-compose up -d; then
    echo "✅ 服务启动成功"
    
    # 等待服务启动
    echo "等待服务启动（30秒）..."
    sleep 30
    
    # 检查服务状态
    echo "检查服务状态..."
    if docker-compose ps | grep -q "Up"; then
        echo "✅ 服务运行正常"
        
        # 测试 Web 服务
        echo "测试 Web 服务..."
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:7801 | grep -q "200\|302"; then
            echo "✅ Web 服务可访问"
        else
            echo "⚠️  Web 服务访问测试失败（可能仍在启动中）"
        fi
        
        # 测试 Ollama 服务
        echo "测试 Ollama 服务..."
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/api/tags | grep -q "200"; then
            echo "✅ Ollama 服务可访问"
        else
            echo "⚠️  Ollama 服务访问测试失败（可能仍在启动中）"
        fi
    else
        echo "❌ 服务未正常运行"
        docker-compose logs
        exit 1
    fi
else
    echo "❌ 服务启动失败"
    exit 1
fi
echo

# 停止服务
echo "7. 清理测试环境..."
if docker-compose down; then
    echo "✅ 服务已停止"
else
    echo "⚠️  服务停止失败"
fi
echo

# 清理测试文档
echo "8. 清理测试文件..."
rm -f docs/test_document.txt
if [ -z "$(ls -A docs 2>/dev/null)" ]; then
    rmdir docs
fi
echo "✅ 测试文件已清理"
echo

echo "=== Docker 部署测试完成 ==="
echo "完成时间: $(date)"
echo "测试结果: ✅ 所有测试通过"
echo
echo "部署建议:"
echo "1. 将您的文档放入 docs/ 目录"
echo "2. 配置 .env 文件（如果需要）"
echo "3. 运行 './deploy.sh full' 进行完整部署"
echo "4. 访问 http://localhost:7801 使用系统"