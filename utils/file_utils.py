"""
文件操作工具函数
提供安全的文件操作和验证功能
"""

import os
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Union, Tuple
from datetime import datetime

from core.exceptions import DocumentError, ConfigError


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建
    Args:
        directory_path: 目录路径
    Returns:
        创建或存在的目录路径
    Raises:
        ConfigError: 如果无法创建目录
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise ConfigError(
            f"无法创建目录: {directory_path}",
            config_key="directory_path",
            details={"error": str(e)}
        )


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    获取文件大小（字节）
    Args:
        file_path: 文件路径
    Returns:
        文件大小（字节）
    Raises:
        DocumentError: 如果文件不存在或无法访问
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise DocumentError(f"文件不存在: {file_path}")
        return path.stat().st_size
    except Exception as e:
        raise DocumentError(
            f"无法获取文件大小: {file_path}",
            file_path=str(file_path),
            details={"error": str(e)}
        )


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为可读格式
    Args:
        size_bytes: 文件大小（字节）
    Returns:
        格式化后的文件大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    获取文件扩展名（小写）
    Args:
        file_path: 文件路径
    Returns:
        文件扩展名（小写，包含点）
    """
    path = Path(file_path)
    return path.suffix.lower()


def is_supported_file(file_path: Union[str, Path], supported_extensions: List[str]) -> bool:
    """
    检查文件是否支持
    Args:
        file_path: 文件路径
        supported_extensions: 支持的扩展名列表
    Returns:
        是否支持该文件
    """
    extension = get_file_extension(file_path)
    return extension in supported_extensions


def list_files_in_directory(
    directory: Union[str, Path],
    extensions: Optional[List[str]] = None,
    recursive: bool = False
) -> List[Path]:
    """
    列出目录中的文件
    Args:
        directory: 目录路径
        extensions: 过滤的扩展名列表，如果为 None 则返回所有文件
        recursive: 是否递归搜索
    Returns:
        文件路径列表
    Raises:
        ConfigError: 如果目录不存在或无法访问
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            raise ConfigError(f"目录不存在: {directory}")
        
        if not dir_path.is_dir():
            raise ConfigError(f"路径不是目录: {directory}")
        
        files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                if extensions is None:
                    files.append(file_path)
                else:
                    if get_file_extension(file_path) in extensions:
                        files.append(file_path)
        
        return sorted(files)
    except Exception as e:
        raise ConfigError(
            f"无法列出目录文件: {directory}",
            config_key="directory",
            details={"error": str(e)}
        )


def safe_delete_file(file_path: Union[str, Path], backup: bool = True) -> bool:
    """
    安全删除文件（可选备份）
    Args:
        file_path: 文件路径
        backup: 是否先备份
    Returns:
        是否成功删除
    Raises:
        DocumentError: 如果文件操作失败
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            logging.warning(f"文件不存在，无需删除: {file_path}")
            return True
        
        # 如果需要备份
        if backup:
            backup_path = path.with_suffix(f"{path.suffix}.bak")
            try:
                shutil.copy2(path, backup_path)
                logging.info(f"文件已备份: {backup_path}")
            except Exception as e:
                logging.warning(f"文件备份失败: {e}")
        
        # 删除文件
        path.unlink()
        logging.info(f"文件已删除: {file_path}")
        return True
    except Exception as e:
        raise DocumentError(
            f"无法删除文件: {file_path}",
            file_path=str(file_path),
            details={"error": str(e)}
        )


def backup_file(file_path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    备份文件
    Args:
        file_path: 原文件路径
        backup_dir: 备份目录，如果为 None 则使用原文件所在目录
    Returns:
        备份文件路径
    Raises:
        DocumentError: 如果备份失败
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise DocumentError(f"原文件不存在: {file_path}")
        
        # 确定备份目录
        if backup_dir is None:
            backup_dir_path = path.parent
        else:
            backup_dir_path = Path(backup_dir)
            ensure_directory(backup_dir_path)
        
        # 生成备份文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.stem}_{timestamp}{path.suffix}"
        backup_path = backup_dir_path / backup_name
        
        # 复制文件
        shutil.copy2(path, backup_path)
        logging.info(f"文件已备份: {backup_path}")
        
        return backup_path
    except Exception as e:
        raise DocumentError(
            f"无法备份文件: {file_path}",
            file_path=str(file_path),
            details={"error": str(e)}
        )


def calculate_md5(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
    """
    计算文件的 MD5 哈希值
    Args:
        file_path: 文件路径
        chunk_size: 读取块大小
    Returns:
        MD5 哈希值
    Raises:
        DocumentError: 如果无法计算哈希值
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise DocumentError(f"文件不存在: {file_path}")
        
        md5_hash = hashlib.md5()
        
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    except Exception as e:
        raise DocumentError(
            f"无法计算文件 MD5: {file_path}",
            file_path=str(file_path),
            details={"error": str(e)}
        )


def read_text_file(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    errors: str = "replace"
) -> str:
    """
    读取文本文件
    Args:
        file_path: 文件路径
        encoding: 文件编码
        errors: 编码错误处理方式
    Returns:
        文件内容
    Raises:
        DocumentError: 如果无法读取文件
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise DocumentError(f"文件不存在: {file_path}")
        
        with open(path, "r", encoding=encoding, errors=errors) as f:
            content = f.read()
        
        return content
    except UnicodeDecodeError as e:
        raise DocumentError(
            f"文件编码错误: {file_path}",
            file_path=str(file_path),
            details={"encoding": encoding, "error": str(e)}
        )
    except Exception as e:
        raise DocumentError(
            f"无法读取文件: {file_path}",
            file_path=str(file_path),
            details={"error": str(e)}
        )


def write_text_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    backup: bool = True
) -> None:
    """
    写入文本文件
    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 文件编码
        backup: 如果文件存在是否备份
    Raises:
        DocumentError: 如果无法写入文件
    """
    try:
        path = Path(file_path)
        
        # 如果文件存在且需要备份
        if path.exists() and backup:
            backup_file(path)
        
        # 确保目录存在
        ensure_directory(path.parent)
        
        # 写入文件
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        
        logging.info(f"文件已写入: {file_path} ({len(content)} 字符)")
    except Exception as e:
        raise DocumentError(
            f"无法写入文件: {file_path}",
            file_path=str(file_path),
            details={"error": str(e)}
        )


def copy_file_safe(
    source: Union[str, Path],
    destination: Union[str, Path],
    overwrite: bool = False
) -> bool:
    """
    安全复制文件
    Args:
        source: 源文件路径
        destination: 目标文件路径
        overwrite: 是否覆盖已存在的文件
    Returns:
        是否成功复制
    Raises:
        DocumentError: 如果复制失败
    """
    try:
        src_path = Path(source)
        dst_path = Path(destination)
        
        if not src_path.exists():
            raise DocumentError(f"源文件不存在: {source}")
        
        if dst_path.exists() and not overwrite:
            raise DocumentError(f"目标文件已存在: {destination}")
        
        # 确保目标目录存在
        ensure_directory(dst_path.parent)
        
        # 复制文件
        shutil.copy2(src_path, dst_path)
        logging.info(f"文件已复制: {source} -> {destination}")
        
        return True
    except Exception as e:
        raise DocumentError(
            f"无法复制文件: {source} -> {destination}",
            file_path=str(source),
            details={"error": str(e)}
        )


def get_file_info(file_path: Union[str, Path]) -> dict:
    """
    获取文件的详细信息
    Args:
        file_path: 文件路径
    Returns:
        文件信息字典
    Raises:
        DocumentError: 如果无法获取文件信息
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise DocumentError(f"文件不存在: {file_path}")
        
        stat_info = path.stat()
        
        return {
            "path": str(path.absolute()),
            "name": path.name,
            "stem": path.stem,
            "suffix": path.suffix,
            "size_bytes": stat_info.st_size,
            "size_formatted": format_file_size(stat_info.st_size),
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            "md5": calculate_md5(path),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "exists": path.exists(),
        }
    except Exception as e:
        raise DocumentError(
            f"无法获取文件信息: {file_path}",
            file_path=str(file_path),
            details={"error": str(e)}
        )