"""
日志配置模块
提供统一的日志配置和管理
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from .settings import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    console_output: bool = True,
    file_output: bool = True,
) -> logging.Logger:
    """
    设置应用程序日志
    
    Args:
        log_level: 日志级别，如 'DEBUG', 'INFO', 'WARNING', 'ERROR'
        log_file: 日志文件路径，如果为 None 则使用默认路径
        console_output: 是否输出到控制台
        file_output: 是否输出到文件
        
    Returns:
        配置好的根日志记录器
    """
    # 获取配置
    if log_level is None:
        log_level = settings.LOG_LEVEL
    
    if log_file is None:
        log_file = settings.get_log_file_path()
    
    # 创建日志目录
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器（使用 RotatingFileHandler）
    if file_output:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 添加错误日志文件处理器
    error_log_file = settings.get_log_file_path("error")
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_log_file,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # 捕获未处理的异常
    def handle_exception(exc_type, exc_value, exc_traceback):
        """处理未捕获的异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 不记录键盘中断
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        root_logger.critical(
            "未捕获的异常",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称，通常是模块名
        
    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(name)


def log_execution_time(logger: logging.Logger):
    """
    记录函数执行时间的装饰器
    
    Args:
        logger: 日志记录器
        
    Returns:
        装饰器函数
    """
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                logger.debug(f"开始执行函数: {func.__name__}")
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                logger.debug(f"函数 {func.__name__} 执行完成，耗时: {elapsed_time:.3f}秒")
                return result
            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"函数 {func.__name__} 执行失败，耗时: {elapsed_time:.3f}秒，错误: {e}")
                raise
        
        return wrapper
    
    return decorator


class LogContext:
    """
    日志上下文管理器，用于记录代码块的执行
    """
    
    def __init__(self, logger: logging.Logger, message: str, level: int = logging.INFO):
        self.logger = logger
        self.message = message
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log(self.level, f"开始: {self.message}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed_time = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.log(self.level, f"完成: {self.message}，耗时: {elapsed_time:.3f}秒")
        else:
            self.logger.error(f"失败: {self.message}，耗时: {elapsed_time:.3f}秒，错误: {exc_val}")


# 导入 time 模块用于 LogContext
import time


# 初始化默认日志配置
def init_default_logging():
    """初始化默认日志配置"""
    return setup_logging()


# 创建默认的模块日志记录器
logger = get_logger(__name__)