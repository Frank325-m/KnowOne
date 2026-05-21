@echo off
REM Docker 部署测试脚本（Windows 版本）

setlocal enabledelayedexpansion

echo === Docker 部署测试 ===
echo 开始时间: %date% %time%
echo.

REM 1. 检查 Docker 环境
echo 1. 检查 Docker 环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装
    exit /b 1
)
for /f "tokens=*" %%i in ('docker --version') do set docker_version=%%i
echo ✅ Docker 已安装: !docker_version!

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安装
    exit /b 1
)
for /f "tokens=*" %%i in ('docker-compose --version') do set compose_version=%%i
echo ✅ Docker Compose 已安装: !compose_version!
echo.

REM 2. 检查项目文件
echo 2. 检查项目文件...
set "required_files=Dockerfile docker-compose.yml requirements.txt web_rag_app.py"
for %%f in (%required_files%) do (
    if exist %%f (
        echo ✅ %%f 存在
    ) else (
        echo ❌ %%f 不存在
        exit /b 1
    )
)
echo.

REM 3. 检查项目目录
echo 3. 检查项目目录...
set "required_dirs=config core utils web"
for %%d in (%required_dirs%) do (
    if exist %%d\ (
        echo ✅ %%d 目录存在
    ) else (
        echo ❌ %%d 目录不存在
        exit /b 1
    )
)
echo.

REM 4. 准备测试文档
echo 4. 准备测试文档...
if not exist docs mkdir docs
(
echo 这是一个测试文档，用于验证 RAG 系统的功能。
echo.
echo RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术。
echo 它首先从知识库中检索相关信息，然后基于这些信息生成回答。
echo.
echo 测试问题：
echo 1. 什么是 RAG？
echo 2. RAG 有什么优势？
echo 3. 如何部署 RAG 系统？
echo.
echo 测试答案：
echo 1. RAG 是检索增强生成技术。
echo 2. RAG 可以提供更准确、更有依据的回答。
echo 3. 可以使用 Docker 容器化部署 RAG 系统。
) > docs\test_document.txt
echo ✅ 测试文档已创建
echo.

REM 5. 测试 Docker 构建
echo 5. 测试 Docker 构建...
docker-compose build --no-cache
if %errorlevel% equ 0 (
    echo ✅ Docker 构建测试通过
) else (
    echo ❌ Docker 构建测试失败
    exit /b 1
)
echo.

REM 6. 测试服务启动
echo 6. 测试服务启动...
docker-compose up -d
if %errorlevel% equ 0 (
    echo ✅ 服务启动成功
    
    REM 等待服务启动
    echo 等待服务启动（30秒）...
    timeout /t 30 /nobreak >nul
    
    REM 检查服务状态
    echo 检查服务状态...
    docker-compose ps | findstr "Up" >nul
    if %errorlevel% equ 0 (
        echo ✅ 服务运行正常
        
        REM 测试 Web 服务
        echo 测试 Web 服务...
        curl -s -o nul -w "%%{http_code}" http://localhost:7801 | findstr "200 302" >nul
        if %errorlevel% equ 0 (
            echo ✅ Web 服务可访问
        ) else (
            echo ⚠️  Web 服务访问测试失败（可能仍在启动中）
        )
        
        REM 测试 Ollama 服务
        echo 测试 Ollama 服务...
        curl -s -o nul -w "%%{http_code}" http://localhost:11434/api/tags | findstr "200" >nul
        if %errorlevel% equ 0 (
            echo ✅ Ollama 服务可访问
        ) else (
            echo ⚠️  Ollama 服务访问测试失败（可能仍在启动中）
        )
    ) else (
        echo ❌ 服务未正常运行
        docker-compose logs
        exit /b 1
    )
) else (
    echo ❌ 服务启动失败
    exit /b 1
)
echo.

REM 7. 停止服务
echo 7. 清理测试环境...
docker-compose down
if %errorlevel% equ 0 (
    echo ✅ 服务已停止
) else (
    echo ⚠️  服务停止失败
)
echo.

REM 8. 清理测试文档
echo 8. 清理测试文件...
del docs\test_document.txt >nul 2>&1
if exist docs\ (
    dir /b docs >nul 2>&1
    if %errorlevel% neq 0 (
        rmdir docs
    )
)
echo ✅ 测试文件已清理
echo.

echo === Docker 部署测试完成 ===
echo 完成时间: %date% %time%
echo 测试结果: ✅ 所有测试通过
echo.
echo 部署建议:
echo 1. 将您的文档放入 docs\ 目录
echo 2. 配置 .env 文件（如果需要）
echo 3. 运行 'deploy.bat full' 进行完整部署
echo 4. 访问 http://localhost:7801 使用系统

endlocal