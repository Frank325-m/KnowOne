"""
自定义异常类
为 RAG 系统提供专门的异常处理
"""

from typing import Optional, Any


class RAGError(Exception):
    """RAG 系统基础异常类"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        self.message = message
        self.code = code or "RAG_ERROR"
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.code}: {self.message} (详情: {self.details})"
        return f"{self.code}: {self.message}"


# ============ 文档处理异常 ============
class DocumentError(RAGError):
    """文档处理异常"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, details: Optional[Any] = None):
        code = "DOCUMENT_ERROR"
        if file_path:
            message = f"{message} (文件: {file_path})"
        super().__init__(message, code, details)


class DocumentLoadError(DocumentError):
    """文档加载异常"""
    
    def __init__(self, file_path: str, error: Optional[str] = None):
        message = f"无法加载文档"
        details = {"file_path": file_path, "error": error}
        super().__init__(message, "DOCUMENT_LOAD_ERROR", details)


class DocumentFormatError(DocumentError):
    """文档格式异常"""
    
    def __init__(self, file_path: str, expected_format: str, actual_format: Optional[str] = None):
        message = f"文档格式不支持"
        details = {
            "file_path": file_path,
            "expected_format": expected_format,
            "actual_format": actual_format
        }
        super().__init__(message, "DOCUMENT_FORMAT_ERROR", details)


class DocumentEncodingError(DocumentError):
    """文档编码异常"""
    
    def __init__(self, file_path: str, encoding: str, error: Optional[str] = None):
        message = f"文档编码错误"
        details = {"file_path": file_path, "encoding": encoding, "error": error}
        super().__init__(message, "DOCUMENT_ENCODING_ERROR", details)


# ============ 向量数据库异常 ============
class VectorDBError(RAGError):
    """向量数据库异常"""
    
    def __init__(self, message: str, db_path: Optional[str] = None, details: Optional[Any] = None):
        code = "VECTOR_DB_ERROR"
        if db_path:
            message = f"{message} (数据库路径: {db_path})"
        super().__init__(message, code, details)


class VectorDBNotFoundError(VectorDBError):
    """向量数据库未找到异常"""
    
    def __init__(self, db_path: str):
        message = f"向量数据库不存在"
        details = {"db_path": db_path}
        super().__init__(message, "VECTOR_DB_NOT_FOUND", details)


class VectorDBCreationError(VectorDBError):
    """向量数据库创建异常"""
    
    def __init__(self, db_path: str, error: Optional[str] = None):
        message = f"无法创建向量数据库"
        details = {"db_path": db_path, "error": error}
        super().__init__(message, "VECTOR_DB_CREATION_ERROR", details)


class VectorDBQueryError(VectorDBError):
    """向量数据库查询异常"""
    
    def __init__(self, query: str, error: Optional[str] = None):
        message = f"向量数据库查询失败"
        details = {"query": query, "error": error}
        super().__init__(message, "VECTOR_DB_QUERY_ERROR", details)


# ============ 模型相关异常 ============
class ModelError(RAGError):
    """模型相关异常"""
    
    def __init__(self, message: str, model_name: Optional[str] = None, details: Optional[Any] = None):
        code = "MODEL_ERROR"
        if model_name:
            message = f"{message} (模型: {model_name})"
        super().__init__(message, code, details)


class ModelLoadError(ModelError):
    """模型加载异常"""
    
    def __init__(self, model_name: str, error: Optional[str] = None):
        message = f"无法加载模型"
        details = {"model_name": model_name, "error": error}
        super().__init__(message, "MODEL_LOAD_ERROR", details)


class ModelInferenceError(ModelError):
    """模型推理异常"""
    
    def __init__(self, model_name: str, input_data: Optional[Any] = None, error: Optional[str] = None):
        message = f"模型推理失败"
        details = {"model_name": model_name, "input_data": input_data, "error": error}
        super().__init__(message, "MODEL_INFERENCE_ERROR", details)


class EmbeddingError(ModelError):
    """嵌入模型异常"""
    
    def __init__(self, model_name: str, error: Optional[str] = None):
        message = f"嵌入模型处理失败"
        details = {"model_name": model_name, "error": error}
        super().__init__(message, "EMBEDDING_ERROR", details)


# ============ 检索相关异常 ============
class RetrievalError(RAGError):
    """检索相关异常"""
    
    def __init__(self, message: str, query: Optional[str] = None, details: Optional[Any] = None):
        code = "RETRIEVAL_ERROR"
        if query:
            message = f"{message} (查询: {query})"
        super().__init__(message, code, details)


class NoRelevantDocumentsError(RetrievalError):
    """无相关文档异常"""
    
    def __init__(self, query: str, top_k: int):
        message = f"未找到相关文档"
        details = {"query": query, "top_k": top_k}
        super().__init__(message, "NO_RELEVANT_DOCUMENTS", details)


class RetrievalTimeoutError(RetrievalError):
    """检索超时异常"""
    
    def __init__(self, query: str, timeout: float):
        message = f"检索超时"
        details = {"query": query, "timeout": timeout}
        super().__init__(message, "RETRIEVAL_TIMEOUT", details)


# ============ 配置相关异常 ============
class ConfigError(RAGError):
    """配置相关异常"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Any] = None):
        code = "CONFIG_ERROR"
        if config_key:
            message = f"{message} (配置项: {config_key})"
        super().__init__(message, code, details)


class ConfigNotFoundError(ConfigError):
    """配置未找到异常"""
    
    def __init__(self, config_key: str, config_file: Optional[str] = None):
        message = f"配置项未找到"
        details = {"config_key": config_key, "config_file": config_file}
        super().__init__(message, "CONFIG_NOT_FOUND", details)


class ConfigValidationError(ConfigError):
    """配置验证异常"""
    
    def __init__(self, config_key: str, value: Any, expected_type: str):
        message = f"配置值无效"
        details = {
            "config_key": config_key,
            "value": value,
            "expected_type": expected_type
        }
        super().__init__(message, "CONFIG_VALIDATION_ERROR", details)


# ============ 工具函数 ============
def handle_rag_error(func):
    """
    处理 RAG 异常的装饰器
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    import functools
    import logging
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RAGError as e:
            # 记录 RAG 异常
            logging.error(f"RAG 异常: {e}")
            raise
        except Exception as e:
            # 将其他异常转换为 RAGError
            logging.error(f"未处理的异常: {e}")
            raise RAGError(f"系统内部错误: {str(e)}", "INTERNAL_ERROR") from e
    
    return wrapper


def safe_execute(func, default_return=None, *args, **kwargs):
    """
    安全执行函数，捕获异常并返回默认值
    
    Args:
        func: 要执行的函数
        default_return: 异常时返回的默认值
        *args: 函数参数
        **kwargs: 函数关键字参数
        
    Returns:
        函数执行结果或默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        import logging
        logging.warning(f"函数 {func.__name__} 执行失败: {e}")
        return default_return