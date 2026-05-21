#!/bin/bash
# RAG 知识库问答系统部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    log_success "Docker 已安装"
}

# 检查 Docker Compose 是否安装
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    log_success "Docker Compose 已安装"
}

# 检查环境配置文件
check_env() {
    if [ ! -f .env ]; then
        log_warning ".env 文件不存在，创建示例配置文件"
        cp .env.example .env
        log_info "请编辑 .env 文件配置您的环境变量"
    else
        log_success "环境配置文件已存在"
    fi
}

# 检查文档目录
check_docs() {
    if [ ! -d "docs" ]; then
        log_warning "docs 目录不存在，创建空目录"
        mkdir -p docs
        log_info "请将您的文档放入 docs/ 目录"
    else
        doc_count=$(find docs -type f | wc -l)
        log_info "docs 目录中有 $doc_count 个文件"
    fi
}

# 构建镜像
build_images() {
    log_info "开始构建 Docker 镜像..."
    docker-compose build
    log_success "Docker 镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose up -d
    log_success "服务已启动"
    
    # 显示服务状态
    log_info "服务状态:"
    docker-compose ps
    
    # 显示访问信息
    log_info "访问信息:"
    log_info "  - RAG Web 应用: http://localhost:7801"
    log_info "  - Ollama API: http://localhost:11434"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose restart
    log_success "服务已重启"
}

# 查看日志
view_logs() {
    log_info "查看服务日志..."
    docker-compose logs -f
}

# 清理资源
cleanup() {
    log_info "清理 Docker 资源..."
    docker-compose down -v
    docker system prune -f
    log_success "Docker 资源已清理"
}

# 初始化向量数据库
init_vector_db() {
    log_info "初始化向量数据库..."
    docker-compose run --rm vector-db-init
    log_success "向量数据库初始化完成"
}

# 显示帮助
show_help() {
    echo "RAG 知识库问答系统部署脚本"
    echo ""
    echo "用法: ./deploy.sh [命令]"
    echo ""
    echo "命令:"
    echo "  build       构建 Docker 镜像"
    echo "  start       启动服务"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  logs        查看日志"
    echo "  init        初始化向量数据库"
    echo "  clean       清理 Docker 资源"
    echo "  status      查看服务状态"
    echo "  full        完整部署（检查环境 -> 构建 -> 启动）"
    echo "  help        显示此帮助信息"
    echo ""
}

# 查看状态
show_status() {
    log_info "服务状态:"
    docker-compose ps
    
    log_info "容器资源使用:"
    docker stats --no-stream
    
    log_info "访问信息:"
    log_info "  - RAG Web 应用: http://localhost:7801"
    log_info "  - Ollama API: http://localhost:11434"
}

# 完整部署
full_deploy() {
    log_info "开始完整部署流程..."
    check_docker
    check_docker_compose
    check_env
    check_docs
    build_images
    start_services
    log_success "完整部署完成！"
    show_status
}

# 主函数
main() {
    case "$1" in
        build)
            check_docker
            check_docker_compose
            build_images
            ;;
        start)
            check_docker
            check_docker_compose
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            view_logs
            ;;
        init)
            init_vector_db
            ;;
        clean)
            cleanup
            ;;
        status)
            show_status
            ;;
        full)
            full_deploy
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"