@echo off
REM RAG 知识库问答系统 Windows 部署脚本

setlocal enabledelayedexpansion

REM 颜色定义
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "NC=%ESC%[0m"

REM 日志函数
:log_info
    echo %BLUE%[INFO]%NC% %*
    exit /b

:log_success
    echo %GREEN%[SUCCESS]%NC% %*
    exit /b

:log_warning
    echo %YELLOW%[WARNING]%NC% %*
    exit /b

:log_error
    echo %RED%[ERROR]%NC% %*
    exit /b

REM 检查 Docker 是否安装
:check_docker
    docker --version >nul 2>&1
    if %errorlevel% neq 0 (
        call :log_error "Docker 未安装，请先安装 Docker"
        exit /b 1
    )
    call :log_success "Docker 已安装"
    exit /b 0

REM 检查 Docker Compose 是否安装
:check_docker_compose
    docker-compose --version >nul 2>&1
    if %errorlevel% neq 0 (
        call :log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit /b 1
    )
    call :log_success "Docker Compose 已安装"
    exit /b 0

REM 检查环境配置文件
:check_env
    if not exist .env (
        call :log_warning ".env 文件不存在，创建示例配置文件"
        if exist .env.example (
            copy .env.example .env >nul
            call :log_info "请编辑 .env 文件配置您的环境变量"
        ) else (
            call :log_error ".env.example 文件不存在"
            exit /b 1
        )
    ) else (
        call :log_success "环境配置文件已存在"
    )
    exit /b 0

REM 检查文档目录
:check_docs
    if not exist docs (
        call :log_warning "docs 目录不存在，创建空目录"
        mkdir docs >nul 2>&1
        call :log_info "请将您的文档放入 docs\ 目录"
    ) else (
        set "doc_count=0"
        for /f %%i in ('dir /b /a-d docs 2^>nul ^| find /c /v ""') do set doc_count=%%i
        call :log_info "docs 目录中有 !doc_count! 个文件"
    )
    exit /b 0

REM 构建镜像
:build_images
    call :log_info "开始构建 Docker 镜像..."
    docker-compose build
    if %errorlevel% equ 0 (
        call :log_success "Docker 镜像构建完成"
    ) else (
        call :log_error "Docker 镜像构建失败"
        exit /b 1
    )
    exit /b 0

REM 启动服务
:start_services
    call :log_info "启动服务..."
    docker-compose up -d
    if %errorlevel% equ 0 (
        call :log_success "服务已启动"
    ) else (
        call :log_error "服务启动失败"
        exit /b 1
    )
    
    REM 显示服务状态
    call :log_info "服务状态:"
    docker-compose ps
    
    REM 显示访问信息
    call :log_info "访问信息:"
    call :log_info "  - RAG Web 应用: http://localhost:7801"
    call :log_info "  - Ollama API: http://localhost:11434"
    exit /b 0

REM 停止服务
:stop_services
    call :log_info "停止服务..."
    docker-compose down
    if %errorlevel% equ 0 (
        call :log_success "服务已停止"
    ) else (
        call :log_error "服务停止失败"
    )
    exit /b 0

REM 重启服务
:restart_services
    call :log_info "重启服务..."
    docker-compose restart
    if %errorlevel% equ 0 (
        call :log_success "服务已重启"
    ) else (
        call :log_error "服务重启失败"
    )
    exit /b 0

REM 查看日志
:view_logs
    call :log_info "查看服务日志..."
    docker-compose logs -f
    exit /b 0

REM 清理资源
:cleanup
    call :log_info "清理 Docker 资源..."
    docker-compose down -v
    docker system prune -f
    call :log_success "Docker 资源已清理"
    exit /b 0

REM 初始化向量数据库
:init_vector_db
    call :log_info "初始化向量数据库..."
    docker-compose run --rm vector-db-init
    if %errorlevel% equ 0 (
        call :log_success "向量数据库初始化完成"
    ) else (
        call :log_error "向量数据库初始化失败"
    )
    exit /b 0

REM 显示状态
:show_status
    call :log_info "服务状态:"
    docker-compose ps
    
    call :log_info "容器资源使用:"
    docker stats --no-stream
    
    call :log_info "访问信息:"
    call :log_info "  - RAG Web 应用: http://localhost:7801"
    call :log_info "  - Ollama API: http://localhost:11434"
    exit /b 0

REM 完整部署
:full_deploy
    call :log_info "开始完整部署流程..."
    call :check_docker
    if %errorlevel% neq 0 exit /b 1
    
    call :check_docker_compose
    if %errorlevel% neq 0 exit /b 1
    
    call :check_env
    call :check_docs
    call :build_images
    call :start_services
    call :log_success "完整部署完成！"
    call :show_status
    exit /b 0

REM 显示帮助
:show_help
    echo RAG 知识库问答系统部署脚本
    echo.
    echo 用法: deploy.bat [命令]
    echo.
    echo 命令:
    echo   build       构建 Docker 镜像
    echo   start       启动服务
    echo   stop        停止服务
    echo   restart     重启服务
    echo   logs        查看日志
    echo   init        初始化向量数据库
    echo   clean       清理 Docker 资源
    echo   status      查看服务状态
    echo   full        完整部署（检查环境 -^> 构建 -^> 启动）
    echo   help        显示此帮助信息
    echo.
    exit /b 0

REM 主函数
:main
    if "%~1"=="" goto show_help
    
    if "%~1"=="build" (
        call :check_docker
        if %errorlevel% neq 0 exit /b 1
        call :check_docker_compose
        if %errorlevel% neq 0 exit /b 1
        call :build_images
    ) else if "%~1"=="start" (
        call :check_docker
        if %errorlevel% neq 0 exit /b 1
        call :check_docker_compose
        if %errorlevel% neq 0 exit /b 1
        call :start_services
    ) else if "%~1"=="stop" (
        call :stop_services
    ) else if "%~1"=="restart" (
        call :restart_services
    ) else if "%~1"=="logs" (
        call :view_logs
    ) else if "%~1"=="init" (
        call :init_vector_db
    ) else if "%~1"=="clean" (
        call :cleanup
    ) else if "%~1"=="status" (
        call :show_status
    ) else if "%~1"=="full" (
        call :full_deploy
    ) else if "%~1"=="help" (
        call :show_help
    ) else (
        echo 未知命令: %~1
        call :show_help
    )
    exit /b 0

REM 执行主函数
call :main %*
endlocal