"""
文档加载和处理工具模块
处理各种格式文档的加载、清理和分割
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Union
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)

from config.settings import settings
from config.logging_config import get_logger
from utils.file_utils import (
    ensure_directory,
    get_file_size,
    format_file_size,
    is_supported_file,
    list_files_in_directory
)
from core.exceptions import (
    DocumentError,
    DocumentLoadError,
    DocumentFormatError,
    DocumentEncodingError,
    handle_rag_error
)

# 获取日志记录器
logger = get_logger(__name__)


@handle_rag_error
def load_single_file(file_path: Union[str, Path]) -> List[Document]:
    """
    加载单文件，自动匹配格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        文档列表
        
    Raises:
        DocumentFormatError: 如果文件格式不支持
        DocumentLoadError: 如果文件加载失败
        DocumentEncodingError: 如果文件编码错误
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DocumentLoadError(
                file_path=str(file_path),
                error="文件不存在"
            )
        
        # 检查文件是否支持
        if not is_supported_file(file_path, settings.SUPPORTED_EXTENSIONS):
            raise DocumentFormatError(
                file_path=str(file_path),
                expected_format=", ".join(settings.SUPPORTED_EXTENSIONS)
            )
        
        file_size = get_file_size(file_path)
        logger.info(f"正在加载文件: {file_path.name} ({format_file_size(file_size)})")
        
        suffix = file_path.suffix.lower()
        
        # 根据文件类型选择合适的加载器
        if suffix == ".txt":
            try:
                loader = TextLoader(str(file_path), encoding="utf-8")
                docs = loader.load()
            except UnicodeDecodeError as e:
                # 尝试其他编码
                try:
                    loader = TextLoader(str(file_path), encoding="gbk")
                    docs = loader.load()
                except UnicodeDecodeError:
                    raise DocumentEncodingError(
                        file_path=str(file_path),
                        encoding="utf-8/gbk",
                        error=str(e)
                    )
        elif suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
        elif suffix == ".docx":
            loader = Docx2txtLoader(str(file_path))
            docs = loader.load()
        else:
            # 这不应该发生，因为前面已经检查过了
            raise DocumentFormatError(
                file_path=str(file_path),
                expected_format=", ".join(settings.SUPPORTED_EXTENSIONS)
            )
        
        # 验证加载结果
        if not docs:
            logger.warning(f"文件加载成功但内容为空: {file_path.name}")
        else:
            total_chars = sum(len(doc.page_content) for doc in docs)
            logger.info(f"文件加载成功: {file_path.name} ({len(docs)} 个文档片段，{total_chars} 字符)")
        
        return docs
        
    except (DocumentFormatError, DocumentLoadError, DocumentEncodingError) as e:
        raise e
    except Exception as e:
        logger.error(f"文件加载失败: {file_path} - {e}")
        raise DocumentLoadError(
            file_path=str(file_path),
            error=str(e)
        )


@handle_rag_error
def load_all_docs(
    folder_path: Optional[Union[str, Path]] = None,
    recursive: bool = True
) -> List[Document]:
    """
    加载指定目录下的所有文档
    
    Args:
        folder_path: 文档目录路径，如果为 None 则使用配置中的目录
        recursive: 是否递归搜索子目录
        
    Returns:
        所有文档的列表
        
    Raises:
        DocumentError: 如果文档加载过程中出现错误
    """
    try:
        if folder_path is None:
            folder_path = settings.docs_dir_abs
        
        folder_path = Path(folder_path)
        
        # 确保目录存在
        ensure_directory(folder_path)
        
        logger.info(f"开始加载文档目录: {folder_path}")
        logger.info(f"支持的文件格式: {', '.join(settings.SUPPORTED_EXTENSIONS)}")
        
        # 列出所有支持的文件
        all_files = list_files_in_directory(
            folder_path,
            extensions=settings.SUPPORTED_EXTENSIONS,
            recursive=recursive
        )
        
        if not all_files:
            logger.warning(f"目录中没有找到支持的文档文件: {folder_path}")
            return []
        
        logger.info(f"找到 {len(all_files)} 个文档文件")
        
        all_docs = []
        failed_files = []
        
        # 逐个加载文件
        for file_path in all_files:
            try:
                doc_list = load_single_file(file_path)
                all_docs.extend(doc_list)
                logger.debug(f"✓ {file_path.name} 加载成功 ({len(doc_list)} 片段)")
            except Exception as e:
                failed_files.append((file_path.name, str(e)))
                logger.warning(f"✗ {file_path.name} 加载失败: {e}")
        
        # 统计信息
        total_chars = sum(len(doc.page_content) for doc in all_docs)
        logger.info(f"文档加载完成，成功: {len(all_docs)} 片段，总字符数: {total_chars}")
        
        if failed_files:
            logger.warning(f"有 {len(failed_files)} 个文件加载失败")
            for file_name, error in failed_files:
                logger.debug(f"  失败文件: {file_name} - {error}")
        
        if not all_docs:
            logger.error("所有文件加载失败，没有可用的文档内容")
            raise DocumentError("没有可用的文档内容")
        
        return all_docs
        
    except Exception as e:
        logger.error(f"文档目录加载失败: {e}")
        raise DocumentError(
            message="无法加载文档目录",
            details={"folder_path": str(folder_path), "error": str(e)}
        )


@handle_rag_error
def clean_text(text: str) -> str:
    """
    清理文本中的特殊字符和多余空格
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    try:
        if not text or not text.strip():
            return ""
        
        original_length = len(text)
        
        # 去除换行与制表符（替换为空格）
        text = text.replace("\n", " ").replace("\t", " ")
        
        # 去除多个连续空格
        text = re.sub(r"\s+", " ", text)
        
        # 去除页码（如 "第1页"、"Page 1" 等）
        text = re.sub(r"(第[0-9]{1,3}页|Page\s*[0-9]{1,3})", "", text, flags=re.IGNORECASE)
        
        # 去除特殊乱码字符（保留中文、英文、数字、标点符号和空格）
        # 保留的字符：中文、英文、数字、常见标点符号
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s\.,;:!?，。；：！？\"'\"()\[\]{}《》<>]", "", text)
        
        # 去除首尾空格
        text = text.strip()
        
        cleaned_length = len(text)
        if cleaned_length < original_length:
            logger.debug(f"文本清理: {original_length} -> {cleaned_length} 字符")
        
        return text
        
    except Exception as e:
        logger.warning(f"文本清理失败: {e}")
        return text  # 返回原始文本


@handle_rag_error
def clean_documents(docs: List[Document], min_length: int = 10) -> List[Document]:
    """
    清理文档列表中的文本
    
    Args:
        docs: 原始文档列表
        min_length: 最小文档长度（字符数）
        
    Returns:
        清理后的文档列表
        
    Raises:
        DocumentError: 如果清理过程中出现错误
    """
    try:
        if not docs:
            logger.warning("文档列表为空，无需清理")
            return []
        
        logger.info(f"开始文档清理，原始文档数: {len(docs)}")
        
        cleaned_docs = []
        removed_count = 0
        
        for i, doc in enumerate(docs):
            try:
                # 清理文本内容
                original_content = doc.page_content
                cleaned_content = clean_text(original_content)
                
                # 创建新的文档对象，保留元数据
                cleaned_doc = Document(
                    page_content=cleaned_content,
                    metadata=doc.metadata.copy() if doc.metadata else {}
                )
                
                # 检查文档长度
                if len(cleaned_content) >= min_length:
                    cleaned_docs.append(cleaned_doc)
                else:
                    removed_count += 1
                    logger.debug(f"文档过短被过滤: {len(cleaned_content)} 字符 (最小要求: {min_length})")
                
            except Exception as e:
                logger.warning(f"文档清理失败 (索引 {i}): {e}")
                # 保留原始文档
                cleaned_docs.append(doc)
        
        # 统计信息
        total_chars = sum(len(doc.page_content) for doc in cleaned_docs)
        logger.info(f"文档清理完成，清理后: {len(cleaned_docs)} 文档，过滤: {removed_count} 文档，总字符数: {total_chars}")
        
        if not cleaned_docs:
            logger.error("所有文档都被过滤，没有可用的内容")
            raise DocumentError("文档清理后没有可用的内容")
        
        return cleaned_docs
        
    except Exception as e:
        logger.error(f"文档清理失败: {e}")
        raise DocumentError(
            message="文档清理失败",
            details={"error": str(e)}
        )


@handle_rag_error
def split_documents(
    docs: List[Document],
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    separators: Optional[List[str]] = None
) -> List[Document]:
    """
    将文档列表进行分块
    
    Args:
        docs: 文档列表
        chunk_size: 单块字符长度
        chunk_overlap: 重叠字符长度
        separators: 分割符列表
        
    Returns:
        分割后的文档列表
        
    Raises:
        DocumentError: 如果分割过程中出现错误
    """
    try:
        if not docs:
            logger.warning("文档列表为空，无需分割")
            return []
        
        # 使用配置值或参数值
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = settings.CHUNK_OVERLAP
        if separators is None:
            separators = settings.SEPARATORS
        
        logger.info(f"开始文档分割，配置: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        logger.debug(f"分割符: {separators}")
        
        # 创建文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            separators=separators,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )
        
        # 执行分割
        split_docs = text_splitter.split_documents(docs)
        
        # 统计信息
        original_count = len(docs)
        split_count = len(split_docs)
        total_chars = sum(len(doc.page_content) for doc in split_docs)
        
        logger.info(f"文档分割完成，原始: {original_count} 文档 -> 分割后: {split_count} 块，总字符数: {total_chars}")
        
        if not split_docs:
            logger.error("文档分割后没有内容")
            raise DocumentError("文档分割后没有内容")
        
        # 分析块大小分布
        chunk_sizes = [len(doc.page_content) for doc in split_docs]
        avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
        max_size = max(chunk_sizes) if chunk_sizes else 0
        min_size = min(chunk_sizes) if chunk_sizes else 0
        
        logger.debug(f"块大小统计: 平均={avg_size:.1f}, 最大={max_size}, 最小={min_size}")
        
        return split_docs
        
    except Exception as e:
        logger.error(f"文档分割失败: {e}")
        raise DocumentError(
            message="文档分割失败",
            details={"error": str(e)}
        )


@handle_rag_error
def process_documents_pipeline(
    folder_path: Optional[Union[str, Path]] = None,
    clean: bool = True,
    split: bool = True,
    min_length: int = 10
) -> List[Document]:
    """
    完整的文档处理管道：加载 -> 清理 -> 分割
    
    Args:
        folder_path: 文档目录路径
        clean: 是否执行清理
        split: 是否执行分割
        min_length: 最小文档长度
        
    Returns:
        处理后的文档列表
    """
    try:
        logger.info("开始文档处理管道")
        
        # 1. 加载文档
        docs = load_all_docs(folder_path)
        
        if not docs:
            logger.error("文档加载阶段失败：没有可用的文档")
            return []
        
        # 2. 清理文档
        if clean:
            docs = clean_documents(docs, min_length=min_length)
        
        if not docs:
            logger.error("文档清理阶段失败：清理后没有可用的文档")
            return []
        
        # 3. 分割文档
        if split:
            docs = split_documents(docs)
        
        if not docs:
            logger.error("文档分割阶段失败：分割后没有可用的文档")
            return []
        
        # 最终统计
        total_chars = sum(len(doc.page_content) for doc in docs)
        logger.info(f"文档处理管道完成，最终文档数: {len(docs)}，总字符数: {total_chars}")
        
        return docs
        
    except Exception as e:
        logger.error(f"文档处理管道失败: {e}")
        raise DocumentError(
            message="文档处理管道失败",
            details={"error": str(e)}
        )


@handle_rag_error
def get_document_stats(docs: List[Document]) -> dict:
    """
    获取文档统计信息
    
    Args:
        docs: 文档列表
        
    Returns:
        统计信息字典
    """
    try:
        if not docs:
            return {
                "count": 0,
                "total_chars": 0,
                "avg_chars": 0,
                "max_chars": 0,
                "min_chars": 0
            }
        
        # 计算统计信息
        char_counts = [len(doc.page_content) for doc in docs]
        total_chars = sum(char_counts)
        avg_chars = total_chars / len(docs) if docs else 0
        max_chars = max(char_counts) if char_counts else 0
        min_chars = min(char_counts) if char_counts else 0
        
        # 获取元数据信息
        sources = set()
        for doc in docs:
            if doc.metadata and "source" in doc.metadata:
                sources.add(doc.metadata["source"])
        
        stats = {
            "count": len(docs),
            "total_chars": total_chars,
            "avg_chars": round(avg_chars, 1),
            "max_chars": max_chars,
            "min_chars": min_chars,
            "unique_sources": len(sources),
            "sources": list(sources)[:10]  # 只显示前10个源
        }
        
        logger.debug(f"文档统计: {stats}")
        return stats
        
    except Exception as e:
        logger.warning(f"获取文档统计失败: {e}")
        return {"error": str(e)}